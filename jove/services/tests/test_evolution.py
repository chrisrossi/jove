import mock
import unittest2

from jove.scripts.tests.test_base import TestBase

# this is a full on integration test


class TestEvolution(TestBase):
    zodb_uri = 'file://%(here)s/../var/Data.fs'

    def test_bootstrap(self):
        self.call_script('evolve', 'test', 'status')
        self.assertEqual(self.output,
            "Package jove.services.tests.fixtures.one\n"
            "Code at software version 6\n"
            "Database at version 6\n"
            "Nothing to do\n"
            "\n"
            "Package jove.services.tests.fixtures.two\n"
            "Code at software version 5\n"
            "Database at version 5\n"
            "Nothing to do\n"
            "\n")

    def test_init(self):
        with mock.patch('jove.tests.test_functional.TestApplication.services',
                        mock.Mock(return_value=[])):
            self.call_script('settings', 'list', 'test')
        self.call_script('evolve', 'test', 'status')
        self.assertEqual(self.error, "Evolution is not initialized.")
        self.call_script('evolve', 'test', 'init')
        self.assertEqual(self.output,
            "Package jove.services.tests.fixtures.one\n"
            "Code at software version 6\n"
            "Database at version 6\n"
            "Nothing to do\n"
            "\n"
            "Package jove.services.tests.fixtures.two\n"
            "Code at software version 5\n"
            "Database at version 5\n"
            "Nothing to do\n"
            "\n")
        self.call_script('evolve', 'test', 'init')
        self.assertEqual(self.error, "Evolution is already initialized.")

    def test_db_version(self):
        self.call_script('evolve', 'test', 'db_version')
        self.assertEqual(self.error,
            'Ambiguous package: must specify --package if more than one '
            'package is configured for evolution.')
        self.call_script('evolve', 'test', 'db_version', '-p', 'foo')
        self.assertEqual(self.error,
            "Package foo is not configured for evolution or is not "
            "initialized.")
        self.call_script('evolve', 'test', 'db_version', '-p',
                         'jove.services.tests.fixtures.one')
        self.assertEqual(self.output, '6\n')

    def test_sw_version(self):
        with mock.patch('jove.tests.test_functional.TestApplication.services',
            mock.Mock(return_value=[(
                'jove#evolution',
                'jove.services.tests.fixtures.two')])):
            self.call_script('evolve', 'test', 'sw_version', '-p', 'foo')
            self.assertEqual(self.error,
                "Package foo is not configured for evolution or is not "
                "initialized.")
            self.call_script('evolve', 'test', 'sw_version')
            self.assertEqual(self.output, '5\n')

    def test_set_version_back(self):
        self.call_script('evolve', 'test', 'set_version', '-p', 'foo', '4')
        self.assertEqual(self.error,
            "Package foo is not configured for evolution or is not "
            "initialized.")
        self.call_script('evolve', 'test', 'set_version', '-p',
                         'jove.services.tests.fixtures.one', '4')
        self.assertEqual(self.output,
            "Package jove.services.tests.fixtures.one\n"
            "Code at software version 6\n"
            "Database at version 4\n"
            "Evolution required\n"
            "\n")
        self.call_script('evolve', 'test', 'db_version', '-p',
                         'jove.services.tests.fixtures.one')
        self.assertEqual(self.output, '4\n')
        self.call_script('evolve', 'test', 'required')
        self.assertEqual(self.output, 'True\n')

    def test_set_version_forward(self):
        self.call_script('evolve', 'test', 'set_version', '-p',
                         'jove.services.tests.fixtures.one', '7')
        self.assertEqual(self.output,
            "Package jove.services.tests.fixtures.one\n"
            "Code at software version 6\n"
            "Database at version 7\n"
            "WARNING: Database is ahead of software\n"
            "\n")
        self.call_script('evolve', 'test', 'db_version', '-p',
                         'jove.services.tests.fixtures.one')
        self.assertEqual(self.output, '7\n')
        self.call_script('evolve', 'test', 'required')
        self.assertEqual(self.output, 'False\n')

    def test_evolve(self):
        self.call_script('evolve', 'test', 'set_version', '-p',
                         'jove.services.tests.fixtures.one', '4')
        self.call_script('evolve', 'test', 'latest', '-p', 'foo')
        self.assertEqual(self.error,
            "Package foo is not configured for evolution or is not "
            "initialized.")
        self.call_script('evolve', 'test', 'latest')
        self.assertEqual(self.output,
            "Package jove.services.tests.fixtures.one\n"
            "Code at software version 6\n"
            "Database at version 4\n"
            "Evolution required\n"
            "\n"
            "Evolving jove.services.tests.fixtures.one . . .\n"
            "jove.services.tests.fixtures.one successfully evolved.\n"
            "\n"
            "Package jove.services.tests.fixtures.two\n"
            "Code at software version 5\n"
            "Database at version 5\n"
            "Nothing to do\n"
            "\n")
        self.call_script('debug', 'test', '-S', self.test_script)
        output = open(self.test_out).read()
        self.assertEqual(output,
            "one_five: evolved\n"
            "one_six: evolved\n")
