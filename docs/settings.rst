========
Settings
========

Jove can manage settings for a site. If an application has settings it wants
managed by Jove, it returns a `colander schema` from the `settings_schema`
method of its application descriptor. Initial values of those settings for a
new site are returned in a dict from the `initial_settings` method of its
application descriptor. Note that the structure returned by an application's
`initial_settings` must validate according to the schema returned its
`settings_schema` method or Jove will be unable to bootstrap a site for that
application.

Settings may be managed on the command line by invoking the settings subcommand
of the jove command line program::

    $ bin/jove settings --help

See the command line help for more information.
