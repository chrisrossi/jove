from code import interact
import sys

from jove.scripts.utils import get_site_root


def config_parser(name, subparsers):
    parser = subparsers.add_parser(
        name, help='Open a debug session with a site.')
    parser.add_argument('-S', '--script', default=None,
                        help='Script to run. If not specified will start '
                        'an interactive session.')
    parser.add_argument('site', help='Site name.')
    parser.set_defaults(func=main, parser=parser)


def main(args):
    local_ns = {'app': args.app}
    cprt = ('Type "help" for more information. "app" is the Jove Pyramid '
            'application.')
    if args.site.lower() != 'none':
        root, closer = get_site_root(args, args.site)
        cprt += ' "root" is the site root object.'
        local_ns['root'] = root
    script = args.script
    if script is None:
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        interact(banner, local=local_ns)
    else:
        code = compile(open(script).read(), script, 'exec')
        exec code in local_ns
