import mock
import unittest2


class TestRetry(unittest2.TestCase):

    def test_retry(self):
        from jove.scripts.utils import ConflictError
        class Script(object):
            def __init__(self):
                self.n_calls = 0
            def __call__(self, args):
                self.n_calls += 1
                raise ConflictError

        from jove.scripts.utils import retry
        script = Script()
        func = retry(5)(script)
        with self.assertRaises(ConflictError):
            func(None)
        self.assertEqual(script.n_calls, 6)


class TestGetVarDir(unittest2.TestCase):

    def test_configured(self):
        from jove.scripts.utils import get_var_dir
        args = mock.Mock()
        args.app.registry.settings.get.return_value = 'myvar'
        self.assertEqual(get_var_dir(args), 'myvar')
        args.app.registry.settings.get.assert_called_once_with('var')

    @mock.patch('jove.scripts.utils.sys.argv', ['/virtual/env/bin/python'])
    def test_not_configured(self):
        from jove.scripts.utils import get_var_dir
        args = mock.Mock()
        args.app.registry.settings.get.return_value = None
        self.assertEqual(get_var_dir(args), '/virtual/env/var')
        args.app.registry.settings.get.assert_called_once_with('var')


class TestGetPidsDir(unittest2.TestCase):

    def test_configured(self):
        from jove.scripts.utils import get_pids_dir
        args = mock.Mock()
        args.app.registry.settings.get.return_value = 'myvar'
        self.assertEqual(get_pids_dir(args), 'myvar')
        args.app.registry.settings.get.assert_called_once_with('pids')

    @mock.patch('jove.scripts.utils.sys.argv', ['/virtual/env/bin/python'])
    def test_not_configured(self):
        from jove.scripts.utils import get_pids_dir
        args = mock.Mock()
        args.app.registry.settings.get.return_value = None
        self.assertEqual(get_pids_dir(args), '/virtual/env/var/pids')


class TestOnlyOne(unittest2.TestCase):

    @mock.patch('jove.scripts.utils.os.remove')
    @mock.patch('jove.scripts.utils.os.getpid')
    @mock.patch('jove.scripts.utils.os.makedirs')
    @mock.patch('jove.scripts.utils.get_pids_dir')
    def test_no_pidfile(self, get_pids_dir, makedirs, getpid, remove):
        get_pids_dir.return_value = '/var/pids'
        getpid.return_value = 42
        existence = [
            ('/var/pids', False),
            ('/var/pids/foo', False),
        ]
        def exists(path):
            name, retvalue = existence.pop(0)
            self.assertEqual(name, path)
            return retvalue

        from StringIO import StringIO
        from jove.scripts.utils import only_one
        script = mock.Mock()
        func = only_one('foo')(script)
        out = StringIO()

        with mock.patch('jove.scripts.utils.open', create=True) as mock_open:
            with mock.patch('jove.scripts.utils.os.path.exists', exists):
                mock_open.return_value = mock.MagicMock(spec=file)
                mock_open.return_value.__enter__.return_value = out
                func('args')

        script.assert_called_once_with('args')
        self.assertEqual(existence, [])
        self.assertEqual(out.getvalue(), '42\n')
        makedirs.assert_called_once_with('/var/pids')
        remove.assert_called_once_with('/var/pids/foo')

    @mock.patch('jove.scripts.utils.os.remove')
    @mock.patch('jove.scripts.utils.os.getpid')
    @mock.patch('jove.scripts.utils.get_pids_dir')
    def test_stale_pidfile(self, get_pids_dir, getpid, remove):
        get_pids_dir.return_value = '/var/pids'
        getpid.return_value = 42
        existence = [
            ('/var/pids', True),
            ('/var/pids/foo', True),
            ('/proc', True),
            ('/proc/56', False),
        ]
        def exists(path):
            name, retvalue = existence.pop(0)
            self.assertEqual(name, path)
            return retvalue

        from StringIO import StringIO
        out = StringIO()
        def mock_open(path, mode='r'):
            if mode == 'w':
                mock_file = mock.MagicMock(spec=file)
                mock_file.__enter__.return_value = out
                return mock_file
            return StringIO('56\n')

        from jove.scripts.utils import only_one
        script = mock.Mock()
        func = only_one('foo')(script)

        with mock.patch('jove.scripts.utils.open', mock_open, create=True):
            with mock.patch('jove.scripts.utils.os.path.exists', exists):
                func('args')

        script.assert_called_once_with('args')
        self.assertEqual(existence, [])
        self.assertEqual(out.getvalue(), '42\n')
        remove.assert_called_once_with('/var/pids/foo')

    @mock.patch('jove.scripts.utils.sys.exit')
    @mock.patch('jove.scripts.utils.get_pids_dir')
    def test_running_procfs(self, get_pids_dir, exit):
        class Exit(Exception):
            pass
        exit.side_effect = Exit

        get_pids_dir.return_value = '/var/pids'
        existence = [
            ('/var/pids', True),
            ('/var/pids/foo', True),
            ('/proc', True),
            ('/proc/56', True),
        ]
        def exists(path):
            name, retvalue = existence.pop(0)
            self.assertEqual(name, path)
            return retvalue

        from StringIO import StringIO
        def mock_open(path, mode='r'):
            return StringIO('56\n')

        from jove.scripts.utils import only_one
        script = mock.Mock()
        func = only_one('foo')(script)

        with mock.patch('jove.scripts.utils.open', mock_open, create=True):
            with mock.patch('jove.scripts.utils.os.path.exists', exists):
                with self.assertRaises(Exit):
                    func('args')

        self.assertEqual(script.method_calls, [])
        self.assertEqual(existence, [])
        exit.assert_called_once_with(1)

    @mock.patch('jove.scripts.utils.sys.exit')
    @mock.patch('jove.scripts.utils.get_pids_dir')
    def test_running_no_procfs(self, get_pids_dir, exit):
        class Exit(Exception):
            pass
        exit.side_effect = Exit

        get_pids_dir.return_value = '/var/pids'
        existence = [
            ('/var/pids', True),
            ('/var/pids/foo', True),
            ('/proc', False),
        ]
        def exists(path):
            name, retvalue = existence.pop(0)
            self.assertEqual(name, path)
            return retvalue

        from StringIO import StringIO
        def mock_open(path, mode='r'):
            return StringIO('56\n')

        from jove.scripts.utils import only_one
        script = mock.Mock()
        func = only_one('foo')(script)

        with mock.patch('jove.scripts.utils.open', mock_open, create=True):
            with mock.patch('jove.scripts.utils.os.path.exists', exists):
                with self.assertRaises(Exit):
                    func('args')

        self.assertEqual(script.method_calls, [])
        self.assertEqual(existence, [])
        exit.assert_called_once_with(1)
