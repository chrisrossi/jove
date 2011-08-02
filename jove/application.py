from pyramid.config import Configurator
from pyramid.exceptions import NotFound

from jove.site import Sites


def make_app(global_config, **local_config):
    settings = global_config.copy()
    settings.update(local_config)
    config = Configurator()
    config.begin()
    config.add_route('sites', '/*subpath')
    config.add_view(site_dispatch, route_name='sites')
    config.registry.sites = Sites(settings)
    config.end()

    return config.make_wsgi_app()


def site_dispatch(request):
    sites = request.registry.sites
    path = list(request.matchdict.get('subpath'))
    host = request.host

    # Copy request, getting rid of pyramid keys from the environ
    environ = request.environ.copy()
    for key in list(environ.keys()):
        if key.startswith('bfg.'):
            del environ[key]
    request = type(request)(environ)

    # nginx likes to set script name to '/' which screws up everybody
    # trying to write urls and causes them to add an extra slash
    if len(request.script_name) == 1:
        request.script_name = ''

    # See if we're in a virtual hosting environment
    name = sites.get_virtual_host(host)
    if not name and path:
        # We are not in a virtual hosting environment, so the first element of
        # the path_info is the name of the site.
        name = path.pop(0)

        # Get the site to dispatch to
        site = sites.get(name)

        # If we found the site, rewrite paths for subrequest
        if site is not None:
            script_name = '/'.join((request.script_name, name))
            path_info = '/' + '/'.join(path)
            request.script_name = script_name
            request.path_info = path_info

    else:
        # Get the virtual host site to dispatch to
        site = sites.get(name)

    # If we still don't have a site, see if one is defined as the root site.
    if site is None:
        name = sites.root_site
        if name is not None:
            site = sites.get(name)

    if site is None:
        raise NotFound

    return request.get_response(site.pipeline())

