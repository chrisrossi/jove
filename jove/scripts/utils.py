from pyramid.scripting import get_root


def get_site_root(args, name):
    sites = args.app.registry.sites
    site = sites.get(name)
    if site is None:
        args.parser.error("No such site: %s" % name)
    return get_root(site.site())


def get_site_home(args, name):
    root, closer = get_site_root(args, name)
    return root.__home__, closer


