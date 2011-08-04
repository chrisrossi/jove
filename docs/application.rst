============
Applications
============

An application is exposed to `Jove` by registering an entry point in your
project's `setup.py` of type `jove.application` which points to a class which
implements the interface described by `jove.interfaces.Application`.

In your project's `setup.py`::

    setup(name='myproject',
          etc...,
          entry_points = """\
              [jove.application]
              myapp = myproject.application:Application
          """
          )

In your project's `application.py`::

    from jove.interfaces import Application

    from myproject.models.site import make_site

    class MyProject(Application):

        def configure(self, config):
            config.set_session_factory(session_factory)
            config.scan('myproject')

        def make_site(self):
            return make_site()

.. autoclass:: jove.interfaces.Application
    :members:

    .. automethod:: __init__

    .. automethod:: configure

    .. automethod:: make_site

    .. automethod:: settings_schema

    .. automethod:: initial_settings
