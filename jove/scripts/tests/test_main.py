import unittest2
import mock


def mock_abspath(path):
    if path.startswith('/'):
        return path
    return '/abs/path/' + path


class Test_get_default_config(unittest2.TestCase):
    argv = ['/venv/bin/jove', 'foo', 'bar']

    @mock.patch('jove.scripts.main.sys.argv', argv)
    @mock.patch('jove.scripts.main.os.path.exists')
    def test_unable_to_find(self, exists):
        from jove.scripts.main import get_default_config
        assert isinstance(exists, mock.Mock)
        exists_values = [False, False, False]
        def side_effect(*args, **kw):
            return exists_values.pop(0)
        exists.side_effect = side_effect
        with self.assertRaises(ValueError):
            get_default_config()
        self.assertEqual(exists.call_count, 3)
        self.assertEqual(exists.call_args_list, [
            (('jove.ini',), {}),
            (('/venv/etc/jove.ini',), {}),
            (('etc/jove.ini',), {}),
        ])

    @mock.patch('jove.scripts.main.os.path.abspath', mock_abspath)
    @mock.patch('jove.scripts.main.sys.argv', argv)
    @mock.patch('jove.scripts.main.os.path.exists')
    def test_found_in_curdir(self, exists):
        from jove.scripts.main import get_default_config
        assert isinstance(exists, mock.Mock)
        exists_values = [True]
        def side_effect(*args, **kw):
            return exists_values.pop(0)
        exists.side_effect = side_effect
        self.assertEqual(get_default_config(), '/abs/path/jove.ini')
        self.assertEqual(exists.call_count, 1)
        self.assertEqual(exists.call_args_list, [
            (('jove.ini',), {}),
        ])

    @mock.patch('jove.scripts.main.os.path.abspath', mock_abspath)
    @mock.patch('jove.scripts.main.sys.argv', argv)
    @mock.patch('jove.scripts.main.os.path.exists')
    def test_found_in_venv(self, exists):
        from jove.scripts.main import get_default_config
        assert isinstance(exists, mock.Mock)
        exists_values = [False, True]
        def side_effect(*args, **kw):
            return exists_values.pop(0)
        exists.side_effect = side_effect
        self.assertEqual(get_default_config(), '/venv/etc/jove.ini')
        self.assertEqual(exists.call_count, 2)
        self.assertEqual(exists.call_args_list, [
            (('jove.ini',), {}),
            (('/venv/etc/jove.ini',), {}),
        ])

    @mock.patch('jove.scripts.main.os.path.abspath', mock_abspath)
    @mock.patch('jove.scripts.main.sys.argv', argv)
    @mock.patch('jove.scripts.main.os.path.exists')
    def test_found_in_etc(self, exists):
        from jove.scripts.main import get_default_config
        assert isinstance(exists, mock.Mock)
        exists_values = [False, False, True]
        def side_effect(*args, **kw):
            return exists_values.pop(0)
        exists.side_effect = side_effect
        self.assertEqual(get_default_config(), '/abs/path/etc/jove.ini')
        self.assertEqual(exists.call_count, 3)
        self.assertEqual(exists.call_args_list, [
            (('jove.ini',), {}),
            (('/venv/etc/jove.ini',), {}),
            (('etc/jove.ini',), {}),
        ])


class TestDebug(unittest2.TestCase):

    @mock.patch('jove.scripts.main.pdb')
    def test_no_exception(self, pdb):
        from jove.scripts.main import debug
        foo = mock.Mock()
        wrapped = debug(foo)
        wrapped('foo')
        self.assertEqual(foo.call_count, 1)
        self.assertEqual(foo.call_args, (('foo',), {}))
        self.assertEqual(pdb.method_calls, [])

    @mock.patch('jove.scripts.main.pdb')
    def test_exception(self, pdb):
        from jove.scripts.main import debug
        foo = mock.Mock()
        foo.side_effect = Exception('foo')
        wrapped = debug(foo)
        wrapped('foo')
        self.assertEqual(pdb.method_calls, [('post_mortem', (), {})])


class TestMain(unittest2.TestCase):

    @mock.patch('jove.scripts.main.pkg_resources.iter_entry_points')
    def test_duplicate_entry_points(self, iter_eps):
        from jove.scripts.main import main
        iter_eps.return_value = [
            DummyEntryPoint('foo'), DummyEntryPoint('foo')]
        with self.assertRaises(RuntimeError):
            main()


class DummyEntryPoint(object):

    def __init__(self, name):
        self.name = name

    def load(self):
        return self

    def __call__(self, name, subparsers):
        pass


