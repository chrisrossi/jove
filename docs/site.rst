=====
Sites
=====

A site is a particular persistent instance of an application.  Sites are
configured in a .ini file, usually `sites.ini`.  Here is an example
`sites.ini`::

    [site:mysite]
    application = myproject#myapp
    zodb_uri = zeo://localhost:8888/

This defines a site, `mysite`, which uses the app, `myproject#myapp` and
connects to a ZEO server listening on port 8888 for persistence.  The minimum
definition for a site consists of the application to use and a URI to use to
connect to a ZODB for persistence.  `myproject#myapp` is the entry point
defined earlier in the section, `Applications`.

