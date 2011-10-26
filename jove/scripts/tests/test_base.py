import mock
import unittest2


class TestBase(unittest2.TestCase):
    error = None
    zodb_uri = 'memory://'

    def setUp(self):
        import cStringIO
        import os
        import tempfile

        self.tmp = tmp = tempfile.mkdtemp('.jove-tests')
        self.etc = etc = os.path.join(tmp, 'etc')
        os.mkdir(etc)
        var = os.path.join(tmp, 'var')
        os.mkdir(var)
        self.ini_path = os.path.join(etc, 'jove.ini')
        with open(self.ini_path, 'w') as out:
            out.write(jove_ini)
        with open(os.path.join(etc, 'sites.ini'), 'w') as out:
            out.write(sites_ini % self.zodb_uri)

        self.out = cStringIO.StringIO()

        self.test_script = os.path.join(tmp, 'test.py')
        self.test_out = os.path.join(tmp, 'test.out')
        with open(self.test_script, 'w') as out:
            out.write(test_py % self.test_out)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def call_script(self, *args):
        class Stop(Exception):
            pass
        def error(myself, message):
            self.error = message
            raise Stop

        from jove.scripts.main import main
        self.out.truncate(0)
        argv = ('jove', '-C', self.ini_path) + args
        try:
            with mock.patch('jove.scripts.main.argparse.ArgumentParser.error',
                            error):
                main(argv, self.out)
        except Stop:
            pass

    @property
    def output(self):
        return self.out.getvalue()


jove_ini = """\
[app:jove]
use = egg:jove#main
sites_config = %(here)s/sites.ini
"""

sites_ini = """\
[site:test]
application = jove#test_app
zodbconn.uri = %s
"""

test_py = """\
with open('%s', 'w') as out:
    for key in sorted(root):
        print >> out, '%%s: %%s' %% (key, root[key])
"""
