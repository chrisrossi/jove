import ConfigParser
import os
import pkg_resources
import transaction

from persistent.mapping import PersistentMapping
from pyramid.config import Configurator
from repoze.retry import Retry
from repoze.zodbconn.finder import PersistentApplicationFinder

from jove.utils import asbool

APPLICATION_ENTRYPOINT = 'jove.application'
LOCAL_SERVICE_ENTRYPOINT = 'jove.local_service'


class Sites(object):
    root_site = None

    def __init__(self, settings):
        self.settings = settings
        ini_file = settings['sites_config']
        here = os.path.dirname(os.path.abspath(ini_file))
        config = ConfigParser.ConfigParser({'here': here})
        config.read(ini_file)
        sites = {}
        virtual_hosts = {}
        for site_section in config.sections():
            if not site_section.startswith('site:'):
                continue
            name = site_section[5:]
            subs = {'site': name}
            site_settings = settings.copy()
            for section in ('DEFAULT', site_section):
                if not config.has_section(section):
                    continue
                for option in config.options(section):
                    site_settings[option] = config.get(section, option) % subs
            sites[name] = LazySite(name, site_settings)
            virtual_host = site_settings.get('virtual_host')
            if virtual_host:
                for host in virtual_host.split():
                    host = host.strip()
                    virtual_hosts[host] = name
            if asbool(site_settings.get('root', 'false')):
                self.root_site = name

        self.sites = sites
        self.virtual_hosts = virtual_hosts

    def get(self, name):
        return self.sites.get(name)

    def get_virtual_host(self, host):
        return self.virtual_hosts.get(host)

    def close(self):
        for site in self.sites.values():
            site.close()


class LazySite(object):
    _site = None
    _pipeline = None

    def __init__(self, name, settings):
        self.name = name
        self.settings = settings

        ep_dist, ep_name = settings['application'].split('#')
        self.application = pkg_resources.load_entry_point(
            ep_dist, APPLICATION_ENTRYPOINT, ep_name)(settings)

        self.zodb_uri = settings['zodb_uri']
        self.zodb_path = settings.get('zodb_path', '/')


    def site(self):
        # Spin up site.
        application = self.application

        # Initialize services
        self.services = services = []
        for spec, descriptor in application.services():
            ep_dist, ep_name = spec.split('#')
            service = pkg_resources.load_entry_point(
                ep_dist, LOCAL_SERVICE_ENTRYPOINT, ep_name)(descriptor)
            services.append(service)

        # Set up the root factory.
        path = filter(None, self.zodb_path.split('/'))
        def appmaker(root):
            needs_commit = False

            # Find application home, creating folders along the way
            home = root
            for name in path:
                folder = home.get(name)
                if folder is None:
                    home[name] = folder = PersistentMapping()
                    needs_commit = True
                home = folder

            # Create the site root if not already created
            if 'content' not in home:
                self.bootstrap(home)
                needs_commit = True

            if needs_commit:
                transaction.commit()

            return home

        finder = PersistentApplicationFinder(self.zodb_uri, appmaker)
        def get_root(request):
            return finder(request.environ)['content']

        # Get persistent settings
        environ = {}
        home = finder(environ)
        settings = self.settings.copy()
        settings.update(home['settings'])

        # Make sure db connection gets closed
        del home, environ

        # Configure Pyramid application
        config = Configurator(root_factory=get_root, settings=settings)
        config.begin()
        for service in services:
            service.preconfigure(config)
        config.include('pyramid_tm')
        application.configure(config)
        for service in services:
            service.configure(config)
        config.end()

        self._site = site = config.make_wsgi_app()

        def closer():
            db = finder.db
            if db is not None:
                db.close()
                finder.db = None

        site.close = closer
        return site

    def pipeline(self):
        pipeline = self._pipeline
        if pipeline is not None:
            return pipeline

        settings = self.settings
        pipeline = self.application.make_pipeline(self.site())
        n_tries = int(settings.get('repoze.retry.tries', 3))
        pipeline = Retry(pipeline, n_tries)
        self._pipeline = pipeline

        return pipeline

    def close(self):
        site = self._site
        if site is not None:
            site.close()
            self._site = None

    def bootstrap(self, home):
        # Initialize content
        application = self.application
        home['content'] = site = application.make_site()
        site.__home__ = home

        # Initialize settings
        # Serialize/Deserialize forces validation and population of
        # schema defaults, if not included in initial settings.
        persistent_settings = application.initial_settings()
        schema = application.settings_schema()
        persistent_settings = schema.deserialize(
            schema.serialize(persistent_settings))
        home['settings'] = persistent_settings

        # Initialize services
        for service in self.services:
            service.bootstrap(home, site)
