from jove.scripts.tests.test_base import TestBase
import mock

class TestSettings(TestBase):
    # Functional tests

    def test_list(self):
        self.call_script('settings', 'list', 'test')
        self.assertEqual(
            self.out.getvalue(),
            'foo: 3\n'
            'things: []\n'
        )

    def test_set(self):
        self.call_script('settings', 'set', 'test', 'foo', '5')
        self.assertEqual(
            self.out.getvalue(),
            'foo: 5\n'
            'things: []\n'
        )

    def test_set_invalid(self):
        self.call_script('settings', 'set', 'test', 'foo', 'five')
        self.assertEqual(self.out.getvalue(),'')
        self.assertEqual(self.error, '{\'foo\': u\'"five" is not a number\'}')

    def test_set_json(self):
        self.call_script('settings', 'set', '-J', 'test', 'things',
                         '["one", "two"]')
        self.assertEqual(
            self.out.getvalue(),
            "foo: 3\n"
            "things: [u'one', u'two']\n"
        )

    def test_append(self):
        self.call_script('settings', 'append', 'test', 'things', 'cat')
        self.assertEqual(
            self.out.getvalue(),
            "foo: 3\n"
            "things: [u'cat']\n"
        )

    def test_append_json(self):
        self.call_script('settings', 'append', '-J', 'test', 'things', '"cat"')
        self.assertEqual(
            self.out.getvalue(),
            "foo: 3\n"
            "things: [u'cat']\n"
        )

    def test_insert(self):
        settings = {'things': [u'cat']}
        with mock.patch(
            'jove.tests.test_functional.TestApplication.initial_settings',
            mock.Mock(return_value=settings)):
            self.call_script('settings', 'append', 'test', 'things', 'cat')
            self.out.truncate(0)
            self.call_script('settings', 'insert', 'test', 'things', '0', 'dog')
            self.assertEqual(
                self.out.getvalue(),
                "foo: 3\n"
                "things: [u'dog', u'cat']\n"
            )

    def test_insert_invalid(self):
        self.call_script('settings', 'append', 'test', 'things', 'cat')
        self.out.truncate(0)
        self.call_script('settings', 'insert', 'test', 'things', '0', 'foobar')
        self.assertEqual(self.out.getvalue(), '')
        self.assertEqual(self.error, "{'things.0': u'Invalid value'}")

    def test_insert_json(self):
        settings = {'things': [u'cat']}
        with mock.patch(
            'jove.tests.test_functional.TestApplication.initial_settings',
            mock.Mock(return_value=settings)):
            self.call_script('settings', 'insert', '-J', 'test', 'things', '0',
                             '"dog"')
            self.assertEqual(
                self.out.getvalue(),
                "foo: 3\n"
                "things: [u'dog', u'cat']\n"
            )

    def test_remove(self):
        settings = {'things': [u'dog', u'cat']}
        with mock.patch(
            'jove.tests.test_functional.TestApplication.initial_settings',
            mock.Mock(return_value=settings)):
            self.call_script('settings', 'remove', 'test', 'things', '1')
            self.assertEqual(
                self.out.getvalue(),
                "foo: 3\n"
                "things: [u'dog']\n"
            )
