import mock
from jove.scripts.tests.test_base import TestBase


class ServeTests(TestBase):

    def tearDown(self):
        super(TestBase, self).tearDown()
        import os
        del os.environ['PASTE_CONFIG_FILE']

    @mock.patch('jove.scripts.serve.sys.exit')
    @mock.patch('jove.scripts.serve.ServeCommand')
    def test_it(self, serve, exit):
        import os

        self.call_script('--pdb', 'serve')
        self.assertEqual(os.environ['PASTE_CONFIG_FILE'],
                         os.path.join(self.etc, 'jove.ini'))
        self.assertEqual(serve.call_count, 1)
        self.assertEqual(serve.call_args, (('jove serve',), {}))
