import argparse
import pkg_resources
import os
import pdb
import sys

from paste.deploy import loadapp

try:
    from psycopg2.extensions import TransactionRollbackError
except ImportError: #pragma NO COVERAGE
    class TransactionRollbackError(Exception):
        pass

try:
    from ZODB.POSException import ConflictError
except ImportError: #pragma NO COVERAGE
    class ConflictError(Exception):
        pass

try:
    from ZPublisher.Publish import Retry as RetryException
except ImportError: #pragma NO COVERAGE
    class RetryException(Exception):
        pass


retryable = (TransactionRollbackError, ConflictError, RetryException)


def main(argv=sys.argv, out=sys.stdout):
    # Configure argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--appname', metavar='APPLICATION',
                        default='jove', help='Name of Jove app in ini file.')
    parser.add_argument('--pdb', action='store_true', default=False,
                        help='Drop into the debugger if there is an uncaught '
                        'exception.')
    parser.add_argument('--retries', type=int, metavar='NUMBER', default=None,
        help='Number of times to retry if there are database conflict errors.')

    # Load subcommands from entry points
    subparsers = parser.add_subparsers(
        title='command', help='Available commands.')
    eps = [ep for ep in pkg_resources.iter_entry_points('jove.script')]
    eps.sort(key=lambda ep: ep.name)
    ep_names = set()
    for ep in eps:
        if ep.name in ep_names:
            raise RuntimeError('script defined more than once: %s' % ep.name)
        ep_names.add(ep.name)
        ep.load()(ep.name, subparsers)

    # Need to get hold of config necessary to load app before running the
    # argument parser because we want to find configured services and
    # add their commands to the parser.
    appname = 'jove'
    config = None
    raw_args = list(argv)
    argv = [raw_args.pop(0)]
    while raw_args:
        arg = raw_args.pop(0)
        if arg in ('-C', '--config'):
            config = raw_args.pop(0)
        elif arg in ('-A', '--appname'):
            appname = raw_args.pop(0)
        else:
            argv.append(arg)
    if not config:
        config = get_default_config()

    # Load subcommands from configured services.
    app = loadapp('config:%s' % config, appname)
    for site in app.registry.sites.sites.values():
        for service in site.services:
            for name, subparser in service.scripts():
                subparser(name, subparsers)

    args = parser.parse_args(argv[1:])
    args.config = config
    args.app = app
    args.out = out
    try:
        func = args.func
        if args.retries:
            func = retry(args.retries)(func)
        if args.pdb:
            func = debug(func)
        func(args)
    finally:
        sites = getattr(app.registry, 'sites')
        if sites is not None:
            sites.close()


def get_default_config():
    config = 'jove.ini'

    if os.path.exists(config):
        return os.path.abspath(config)

    bin = os.path.abspath(sys.argv[0])
    env = os.path.dirname(os.path.dirname(bin))
    config = os.path.join(env, 'etc', 'jove.ini')

    if os.path.exists(config):
        return config

    config = os.path.join('etc', 'jove.ini')

    if os.path.exists(config):
        return os.path.abspath(config)

    raise ValueError("Unable to locate config.  Use --config to specify "
                     "path to jove.ini")


def debug(f):
    def wrapper(args):
        try:
            return f(args)
        except:
            pdb.post_mortem()
    return wrapper


def retry(n, retryable=retryable):
    def decorator(f):
        def wrapper(args):
            tries = n
            while True:
                try:
                    return f(args)
                except retryable:
                    if not tries:
                        raise
                    tries -= 1
        return wrapper
    return decorator
