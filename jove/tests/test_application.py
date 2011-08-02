import mock
import unittest2


class Test_site_dispatch(unittest2.TestCase):
    """
    Most functionality in site_dispatch is covered by the functional tests, so
    these unittests are primarily for some of the outlier code paths that are
    harder to exercise with the functional tests.
    """

    def setUp(self):
        self.sites = sites = DummySites()
        self.registry = registry = mock.Mock()
        registry.sites = sites

    def callFUT(self, path='/', request=None):
        from jove.application import site_dispatch as fut
        if request is None:
            request = self.makeRequest(path)
        return fut(request)

    def makeRequest(self, path):
        from pyramid.request import Request
        request = Request.blank(path)
        request.registry = self.registry
        subpath = filter(None, path.split('/'))
        request.matchdict = {'subpath': subpath}
        return request

    def test_root_not_found(self):
        from pyramid.exceptions import NotFound
        with self.assertRaises(NotFound):
            self.callFUT()

    def test_script_name_is_slash(self):
        # nginx does this
        request = self.makeRequest('/foo/bar')
        request.script_name = '/'
        response = self.callFUT(request=request)
        self.assertEqual(response.body, 'Hello World')

    def test_virtual_host(self):
        self.sites.virtual_host = 'foo'
        self.sites.app.script_name = ''
        request = self.makeRequest('/bar')
        response = self.callFUT(request=request)
        self.assertEqual(response.body, 'Hello World')


class DummySites(dict):
    root_site = None
    virtual_host = None

    def __init__(self):
        site = mock.Mock()
        pipeline = mock.Mock()
        pipeline.return_value = self.app = DummyApp()
        site.pipeline = pipeline
        self['foo'] = site

    def get_virtual_host(self, name):
        return self.virtual_host


class DummyApp(object):
    script_name = '/foo'
    path_info = '/bar'

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        assert environ['SCRIPT_NAME'] == self.script_name, \
               environ['SCRIPT_NAME']
        assert environ['PATH_INFO'] == self.path_info, \
               environ['PATH_INFO']
        return ['Hello ', 'World']
