import unittest2


class TestBase(unittest2.TestCase):

    def setUp(self):
        import cStringIO
        import os
        import tempfile

        self.tmp = tmp = tempfile.mkdtemp('.jove-tests')
        self.etc = etc = os.path.join(tmp, 'etc')
        os.mkdir(etc)
        var = os.path.join(tmp, 'var')
        self.ini_path = os.path.join(etc, 'jove.ini')
        with open(self.ini_path, 'w') as out:
            out.write(jove_ini)
        with open(os.path.join(etc, 'sites.ini'), 'w') as out:
            out.write(sites_ini)

        self.out = cStringIO.StringIO()

    def tearDown(self):
        import os
        import shutil
        shutil.rmtree(self.tmp)

    def call_script(self, *args):
        import os
        from jove.scripts.main import main
        argv = ('jove', '-C', self.ini_path) + args
        return main(argv, self.out)


jove_ini = """\
[app:jove]
use = egg:jove#main
sites_config = %(here)s/sites.ini
"""

sites_ini = """\
[site:test]
application = jove#test_app
zodbconn.uri = memory://
"""
