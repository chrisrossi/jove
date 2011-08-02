import abc
import colander


"""
Set of abstract base classes which document the expected API of plugpoints for
`Jove`.  These base classes may be extended to create concrete subclasses, and
provide default implementations for some methods.  Use of these base classes is
not required, so long as implementations conform to the interfaces described
here.
"""


class ApplicationDescriptor(object):
    """
    Concrete subclasses of `ApplicationDescriptor` define applications that can
    be run inside of Jove.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, settings):
        """
        Constructs an instance of an application descriptor.  Stores the
        `settings` parameter as the attribute, `settings`, of the instance.
        """
        self.settings = settings

    @abc.abstractmethod
    def configure(self, config):
        """
        Performs the necessary `Pyramid` setup for the application, such
        as registering views, etc... The `config` parameter is an instance of
        `pyramid.config.Configurator`. In general a `Jove` application is
        set up in the same as a `Pyramid` application. See the
        `Pyramid` documentation for more information.  The actual `WSGI`
        application is created by `Jove`.  There is no need to call
        `config.make_wsgi_app()` in this method.  This method has no return
        value.
        """

    @abc.abstractmethod
    def make_site(self):
        """
        This method is responsible for bootstrapping a site which uses this
        application.  This method is expected to return a
        `persistent.Persistent` object which is the initial site root for this
        site.  This is the object that will be returned by the `Pyramid`
        `root factory` configured by `Jove`.
        """

    def make_pipeline(self, app):
        """
        This method can be used to optionally add middleware to the WSGI
        pipeline used by the application.  The `app` parameter is the fully
        configured `Pyramid` WSGI application created by `Jove`.
        Applications which require middleware in the WSGI stick may compose
        their middleware stack in this method and return the resulting
        pipeline, which will also be a WSGI application.  By default this
        method simply returns `app`.
        """
        return app

    def settings_schema(self):
        """
        This function returns a `Colander` schema which describes the settings
        used by this application.  By use of the schema, application settings
        can be handled by Jove's command line and as well as by a hypothetical
        future administrative web interface.
        """
        return colander.Schema()

    def initial_settings(self):
        """
        Returns a `Colander` appstruct which contains initial values for the
        settings used by this application.  The appstruct must be valid
        according to the schema returned by the `settings_schema` method.
        """
        return {}
