import mock

from jove.scripts.tests.test_base import TestBase


class TestDebug(TestBase):
    # Integration test

    @mock.patch('jove.scripts.debug.interact')
    def test_interactive_no_site(self, interact):
        from pyramid.router import Router
        self.call_script('debug', 'None')
        self.assertEqual(interact.call_count, 1)
        banner = interact.call_args[0][0]
        names = interact.call_args[1]['local']
        self.assertIsInstance(names['app'], Router)
        self.assertNotIn('root', names)
        self.assertIn('"app" is the', banner)
        self.assertNotIn('"root" is the', banner)

    @mock.patch('jove.scripts.debug.interact')
    def test_interactive_with_site(self, interact):
        from pyramid.router import Router
        from jove.tests.test_functional import DummySite
        self.call_script('debug', 'test')
        self.assertEqual(interact.call_count, 1)
        banner = interact.call_args[0][0]
        names = interact.call_args[1]['local']
        self.assertIsInstance(names['app'], Router)
        self.assertIsInstance(names['root'], DummySite)
        self.assertIn('"app" is the', banner)
        self.assertIn('"root" is the', banner)

    @mock.patch('jove.scripts.main.argparse.ArgumentParser.error')
    def test_interactive_bad_site(self, error):
        from pyramid.router import Router
        from jove.tests.test_functional import DummySite
        error.side_effect = Exception('bail out')
        self.call_script('debug', 'nosuchsite')
        self.assertEqual(self.error, 'No such site: nosuchsite')

    def test_script(self):
        import os
        root = DummySite()
        get_site_root = mock.Mock(return_value=(root, None))
        script = os.path.join(self.tmp, 'script.py')
        with open(script, 'w') as out:
            print >> out, "root.foo = 'bar'"
        with mock.patch('jove.scripts.debug.get_site_root', get_site_root):
            self.call_script('debug', 'test', '-S', script)
        self.assertEqual(root.foo, 'bar')


class DummySite(object):
    foo = 'foo'
