import colander
import json
import pprint
import transaction

from jove.scripts.utils import get_site_home


def config_parser(name, subparsers):
    parser = subparsers.add_parser(
        name, help='Manage site configuration.')
    subparsers = parser.add_subparsers(
        title='command', help='Settings operations.')
    config_list_settings(subparsers)
    config_set_setting(subparsers)
    config_append_setting(subparsers)
    config_insert_setting(subparsers)
    config_remove_setting(subparsers)


def config_list_settings(subparsers):
    parser = subparsers.add_parser(
        'list', help='List site settings.')
    parser.add_argument('site', metavar='site', help='Site.')
    parser.set_defaults(func=list_settings, parser=parser)


def config_set_setting(subparsers):
    parser = subparsers.add_parser(
        'set', help='Change a configuration setting.')
    parser.add_argument('-J', '--json', action='store_true', default=False,
                        help='Value is a JSON string.')
    parser.add_argument('site', metavar='site', help='Site.')
    parser.add_argument('path', help='Path to setting to change.')
    parser.add_argument('value', help='New value of setting.')
    parser.set_defaults(func=set_setting, parser=parser)


def config_remove_setting(subparsers):
    parser = subparsers.add_parser(
        'remove', help='Remove an item from a list setting.')
    parser.add_argument('site', metavar='site', help='Site.')
    parser.add_argument('path', help='Path to list.')
    parser.add_argument('index', type=int, help='Index of item to remove')
    parser.set_defaults(func=remove_setting, parser=parser)


def config_append_setting(subparsers):
    parser = subparsers.add_parser(
        'append', help='Append an item to a list setting.')
    parser.add_argument('-J', '--json', action='store_true', default=False,
                        help='Value is a JSON string.')
    parser.add_argument('site', metavar='site', help='Site.')
    parser.add_argument('path', help='Path to list.')
    parser.add_argument('value', help='New value to append.')
    parser.set_defaults(func=add_setting, parser=parser)


def config_insert_setting(subparsers):
    parser = subparsers.add_parser(
        'insert', help='Insert an item to a list setting.')
    parser.add_argument('-J', '--json', action='store_true', default=False,
                        help='Value is a JSON string.')
    parser.add_argument('site', metavar='site', help='Site.')
    parser.add_argument('path', help='Path to list.')
    parser.add_argument('index', type=int, help='Index of new item.')
    parser.add_argument('value', help='New value to insert.')
    parser.set_defaults(func=add_setting, parser=parser)


def list_settings(args):
    home, closer = get_site_home(args, args.site)
    _list_settings(home['settings'], args.out)


def _list_settings(settings, out):
    for name, value in sorted(settings.items()):
        key = '%s: ' % name
        out.write(key)
        pprint.pprint(value, out, depth=len(key))


def set_setting(args):
    try:
        value = args.value
        if args.json:
            value = json.loads(value)
        home, closer = get_site_home(args, args.site)
        site = args.app.registry.sites.get(args.site)
        schema = site.application.settings_schema()
        serial = schema.serialize(home['settings'])
        schema.set_value(serial, args.path, value)
        home['settings'] = schema.deserialize(serial)
        transaction.commit()

        _list_settings(home['settings'], args.out)
    except colander.Invalid, e:
        args.parser.error(str(e))


def add_setting(args):
    try:
        value = args.value
        if args.json:
            value = json.loads(value)
        home, closer = get_site_home(args, args.site)
        site = args.app.registry.sites.get(args.site)
        schema = site.application.settings_schema()
        serial = schema.serialize(home['settings'])
        sequence = schema.get_value(serial, args.path)
        index = getattr(args, 'index', None)
        if index is not None:
            sequence.insert(index, value)
        else:
            sequence.append(value)
        home['settings'] = schema.deserialize(serial)
        transaction.commit()

        _list_settings(home['settings'], args.out)
    except colander.Invalid, e:
        args.parser.error(str(e))


def remove_setting(args):
    home, closer = get_site_home(args, args.site)
    site = args.app.registry.sites.get(args.site)
    schema = site.application.settings_schema()
    settings = home['settings']
    sequence = schema.get_value(settings, args.path)
    del sequence[args.index]
    home['settings'] = settings  # Force persistence
    transaction.commit()

    _list_settings(settings, args.out)


