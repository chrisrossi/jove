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

from jove.interfaces import ApplicationDescriptor


class TestApplication(ApplicationDescriptor):

    def configure(self, config):
        config.add_view(dummy_view)
        config.add_view(dummy_edit_view, 'edit')

    def make_site(self):
        return DummySite('Test Application')

    def settings_schema(self):
        return Settings()

    def initial_settings(self):
        return {'things': []}


import persistent

class DummySite(persistent.Persistent):
    __name__ = None
    __parent__ = None

    def __init__(self, body):
        self.body = body


def dummy_view(request):
    from pyramid.response import Response
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
