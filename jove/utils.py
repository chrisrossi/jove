from pyramid.traversal import find_root


def asbool(s):
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')


def find_home(context):
    return find_root(context).__home__
