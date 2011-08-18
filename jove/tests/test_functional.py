import colander
import mock
import os
import shutil
import tempfile
import unittest2
import webtest


class FunctionalTests(unittest2.TestCase):

    def setUp(self):
        self.tmp = tmp = tempfile.mkdtemp('.jove-testing')
        self.etc = etc = os.path.join(tmp, 'etc')
        os.mkdir(etc)
        self.sites_ini = os.path.join(etc, 'sites.ini')
        self.zodb_uri = 'memory://'

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def make_application(self, sites_ini):
        from jove.application import make_app
        with open(self.sites_ini, 'w') as out:
            out.write(sites_ini)
        settings = {'sites_config': self.sites_ini}
        return webtest.TestApp(make_app(settings))

    def assert_site_works(self, app, url):
        if not url.startswith('http:'):
            url = 'http://localhost' + url
        response = app.get(url)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'Test Application')
        response = app.post(url + '/edit', {
            'body': 'Take this test and shove it.'})
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, url)
        response = app.get(response.location)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, 'Take this test and shove it.')

    def test_it(self):
        app = self.make_application(
            "[site:acme]\n"
            "application = jove#test_app\n"
            "zodb_uri = %s\n" % self.zodb_uri)
        self.assert_site_works(app, '/acme/')

    def test_it_ignore_non_site_section(self):
        app = self.make_application(
            "[site:acme]\n"
            "application = jove#test_app\n"
            "zodb_uri = %s\n"
            "[other]\n"
            "ignore = me\n" % self.zodb_uri)
        self.assert_site_works(app, '/acme/')

    def test_root_site(self):
        app = self.make_application(
            "[site:acme]\n"
            "application = jove#test_app\n"
            "zodb_uri = %s\n"
            "root = True\n" % self.zodb_uri)
        self.assert_site_works(app, '/')

    def test_virtual_host(self):
        app = self.make_application(
            "[site:acme]\n"
            "application = jove#test_app\n"
            "zodb_uri = %s\n"
            "virtual_host = acme.com:80\n" % self.zodb_uri)
        self.assert_site_works(app, 'http://acme.com/')

    def test_it_w_zodb_path(self):
        app = self.make_application(
            "[site:acme]\n"
            "application = jove#test_app\n"
            "zodb_path = foo/bar\n"
            "zodb_uri = %s\n" % self.zodb_uri)
        self.assert_site_works(app, '/acme/')

    @mock.patch('jove.site.transaction')
    def test_it_exception_in_bootstrap(self, tx):
        import colander
        import transaction
        def abort():
            tx.aborted = True
            transaction.abort()
        tx.abort = abort
        with mock.patch(
            'jove.tests.test_functional.TestApplication.initial_settings',
            mock.Mock(return_value={})):
            with self.assertRaises(colander.Invalid):
                app = self.make_application(
                    "[site:acme]\n"
                    "application = jove#test_app\n"
                    "zodb_uri = %s\n" % self.zodb_uri)
                self.assert_site_works(app, '/acme/')
        self.assertTrue(tx.aborted)


from jove.interfaces import Application
from jove.interfaces import LocalService


class TestApplication(Application):

    def configure(self, config):
        config.add_view(dummy_view)
        config.add_view(dummy_edit_view, 'edit')

    def make_site(self, home, site):
        return DummySite('Test Application')

    def settings_schema(self):
        return Settings()

    def initial_settings(self):
        return {'things': []}

    def services(self):
        return [('jove#test_local_service', 'Descriptor')]


class TestLocalService(LocalService):

    def __init__(self, descriptor):
        assert descriptor == 'Descriptor'

    def preconfigure(self, config):
        config.registry.pre_foo = 'Pre Foo'

    def configure(self, config):
        config.registry.foo = 'Foo'

    def bootstrap(self, home, site):
        home['LocalService'] = 'Foo'


import persistent

class DummySite(persistent.Persistent):
    __name__ = None
    __parent__ = None

    def __init__(self, body):
        self.body = body


def dummy_view(request):
    from pyramid.response import Response
    from jove.utils import find_home
    assert request.registry.pre_foo == 'Pre Foo'
    assert request.registry.foo == 'Foo'
    assert find_home(request.context)['LocalService'] == 'Foo'
    return Response(request.context.body, content_type='text/plain')


def dummy_edit_view(request):
    from pyramid.httpexceptions import HTTPFound
    from pyramid.url import resource_url
    request.context.body = request.params['body']
    return HTTPFound(resource_url(request.context, request))


@colander.Function
def not_foobar(value):
    return value != 'foobar'


class Vocabulary(colander.SequenceSchema):
    items = colander.SchemaNode(colander.String(), validator=not_foobar)


class Settings(colander.Schema):
    foo = colander.SchemaNode(colander.Int(), default=3)
    things = Vocabulary()
