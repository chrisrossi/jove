import os
import logging
import sys

from pyramid.scripting import get_root

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


def get_site(args, name):
    sites = args.app.registry.sites
    site = sites.get(name)
    if site is None:
        args.parser.error("No such site: %s" % name)
    return site


def get_site_root(args, name):
    return get_root(get_site(args, name).site())


def get_site_home(args, name):
    root, closer = get_site_root(args, name)
    return root.__home__, closer

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


def get_var_dir(args):
    var = args.app.registry.settings.get('var')
    if var:
        return var
    exe = os.path.abspath(sys.argv[0])
    env = os.path.dirname(os.path.dirname(exe))
    return os.path.join(env, 'var')


def get_pids_dir(args):
    pids = args.app.registry.settings.get('pids')
    if pids:
        return pids
    return os.path.join(get_var_dir(args), 'pids')


def only_one(name):
    def decorator(f):
        def wrapper(args):
            pids = get_pids_dir(args)
            if not os.path.exists(pids):
                os.makedirs(pids)
            pidfile = os.path.join(pids, name)
            if os.path.exists(pidfile):
                # pid file exists
                # If using a sane operating system with procfs, we check to see
                # whether process is still actually running.
                log = logging.getLogger(name)
                is_running = True
                pid = open(pidfile).read().strip()
                if os.path.exists('/proc'):
                    is_running = os.path.exists(os.path.join('/proc', pid))
                if is_running:
                    log.warn("%s already running with pid %s" % (name, pid))
                    log.warn("Exiting.")
                    sys.exit(1)
                else:
                    log.warn("Found stale pid file for %s (pid %s)." %
                             (name, pid))
            with open(pidfile, 'w') as out:
                print >> out, str(os.getpid())

            try:
                return f(args)
            finally:
                os.remove(pidfile)

        return wrapper
    return decorator


