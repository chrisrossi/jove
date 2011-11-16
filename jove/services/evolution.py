from persistent.mapping import PersistentMapping

from pyramid.util import DottedNameResolver

from jove.interfaces import LocalService
from jove.scripts.utils import get_site
from jove.scripts.utils import get_site_home

import transaction


HOME_KEY = 'jove.services.evolution'


class EvolutionService(LocalService):

    def __init__(self, pkgname):
        self.pkgname = pkgname

    def scripts(self):
        return [('evolve', config_parser)]

    def __call__(self, home):
        return Evolution(self.pkgname, home)

    def bootstrap(self, home, site):
        self(home)


class Evolution(object):

    def __init__(self, pkgname, home):
        self.pkgname = pkgname
        self.home = home
        self.resolver = resolver = DottedNameResolver(None)
        self.package = resolver.resolve(pkgname)

        if HOME_KEY not in home:
            home[HOME_KEY] = PersistentMapping()
        self.versions = versions = home[HOME_KEY]

        if pkgname not in versions:
            versions[pkgname] = self.software_version()

    def software_version(self):
        return getattr(self.package, 'VERSION')

    def database_version(self):
        return self.versions[self.pkgname]

    def evolution_required(self):
        return self.database_version() < self.software_version()

    def evolve(self):
        pkgname = self.pkgname
        resolve = self.resolver.resolve
        home = self.home
        target = self.software_version()
        for version in xrange(self.database_version() + 1, target + 1):
            module_name = '%s.evolve%d' % (pkgname, version)
            module = resolve(module_name)
            evolve = getattr(module, 'evolve')
            evolve(home)
            self.versions[self.pkgname] = version
            transaction.commit()


#
# Command line interface
#


def config_parser(name, subparsers):
    """
    Configure command line interface.
    """
    parser = subparsers.add_parser(
        name, help='Evolve a site database.')
    parser.add_argument('site', help='Site to evolve.')
    subparsers = parser.add_subparsers(
        title='command', help='Evolution commands.')
    config_init(subparsers)
    config_status(subparsers)
    config_db_version(subparsers)
    config_sw_version(subparsers)
    config_required(subparsers)
    config_set_version(subparsers)
    config_latest(subparsers)


def config_init(subparsers):
    parser = subparsers.add_parser('init', help='Initialize evolution.')
    parser.set_defaults(func=init, parser=parser)


def config_status(subparsers):
    parser = subparsers.add_parser('status', help='Show evolution status.')
    parser.set_defaults(func=status, parser=parser)


def config_db_version(subparsers):
    parser = subparsers.add_parser(
        'db_version', help='Tersely show current database version.')
    parser.add_argument('-p', '--package', metavar='NAME',
        help='Package to check version for. This argument is required if more '
        'than one package is configured for evolution.')
    parser.set_defaults(func=db_version, parser=parser)


def config_sw_version(subparsers):
    parser = subparsers.add_parser(
        'sw_version', help='Tersely show whether evolution is required.')
    parser.add_argument('-p', '--package', metavar='NAME',
        help='Package to check version for. This argument is required if more '
        'than one package is configured for evolution.')
    parser.set_defaults(func=sw_version, parser=parser)


def config_required(subparsers):
    parser = subparsers.add_parser(
        'required', help='Tersely show whether evolution is required.')
    parser.set_defaults(func=required, parser=parser)


def config_set_version(subparsers):
    parser = subparsers.add_parser(
        'set_version', help='Set database version for evolution.')
    parser.add_argument('-p', '--package', metavar='NAME',
        help='Package to set version for. This argument is required if more '
        'than one package is configured for evolution.')
    parser.add_argument('version', type=int, help='The version number to set.')
    parser.set_defaults(func=set_version, parser=parser)


def config_latest(subparsers):
    parser = subparsers.add_parser(
        'latest', help='Upgrade database to latest version.')
    parser.add_argument('-p', '--package', metavar='NAME', action='append',
        help='Package to update. May be specified more than once. By default '
        'all configured packages are updated.')
    parser.set_defaults(func=latest, parser=parser)


def get_services(args):
    site = get_site(args, args.site)
    services = []
    for service in site.services:
        if isinstance(service, EvolutionService):
            services.append(service)
    return services


def init(args):
    home, closer = get_site_home(args, args.site)
    if HOME_KEY in home:
        args.parser.error("Evolution is already initialized.")
    for service in sorted(get_services(args), key=lambda x: x.pkgname):
        evolution = service(home)
        print_status(args, evolution)
    transaction.commit()


def get_versions(args):
    home, closer = get_site_home(args, args.site)
    versions = home.get(HOME_KEY)
    if not versions:
        args.parser.error("Evolution is not initialized.")
    return home, versions, closer


def status(args):
    home, versions, closer = get_versions(args)
    for pkgname in sorted(versions.keys()):
        print_status(args, Evolution(pkgname, home))


def print_status(args, evolution):
    sw = evolution.software_version()
    db = evolution.database_version()
    print >> args.out, "Package %s" % evolution.pkgname
    print >> args.out, "Code at software version %d" % sw
    print >> args.out, "Database at version %d" % db
    if db == sw:
        print >> args.out, "Nothing to do"
    elif db < sw:
        print >> args.out, "Evolution required"
    else:
        print >> args.out, "WARNING: Database is ahead of software"
    print >> args.out, ''


def db_version(args):
    home, versions, closer = get_versions(args)
    pkgname = get_pkgname(args)
    if not pkgname in versions:
        args.parser.error(
            "Package %s is not configured for evolution or is not initialized."
             % pkgname)
    print >> args.out, str(Evolution(pkgname, home).database_version())


def sw_version(args):
    home, versions, closer = get_versions(args)
    pkgname = get_pkgname(args)
    if not pkgname in versions:
        args.parser.error(
            "Package %s is not configured for evolution or is not initialized."
             % pkgname)
    print >> args.out, str(Evolution(pkgname, home).software_version())


def required(args):
    required = False
    home, versions, closer = get_versions(args)
    for pkgname in versions.keys():
        evolution = Evolution(pkgname, home)
        if evolution.evolution_required():
            required = True
            break
    print >> args.out, str(required)


def get_pkgname(args):
    pkgname = args.package
    if not pkgname:
        services = get_services(args)
        if len(services) > 1:
            args.parser.error(
                'Ambiguous package: must specify --package if more than one '
                'package is configured for evolution.')
        pkgname = services[0].pkgname
    return pkgname


def set_version(args):
    home, versions, closer = get_versions(args)
    pkgname = get_pkgname(args)
    if not pkgname in versions:
        args.parser.error(
            "Package %s is not configured for evolution or is not initialized."
             % pkgname)
    versions[pkgname] = args.version
    print_status(args, Evolution(pkgname, home))
    transaction.commit()


def latest(args):
    home, versions, closer = get_versions(args)
    pkgnames = args.package
    if not pkgnames:
        pkgnames = versions.keys()
    for pkgname in sorted(pkgnames):
        if pkgname not in versions:
            args.parser.error(
                "Package %s is not configured for evolution "
                "or is not initialized." % pkgname)
        evolution = Evolution(pkgname, home)
        print_status(args, evolution)
        if evolution.evolution_required():
            print >> args.out, "Evolving %s . . ." % pkgname
            evolution.evolve()
            print >> args.out, "%s successfully evolved." % pkgname
            print >> args.out, ''

    transaction.commit()
