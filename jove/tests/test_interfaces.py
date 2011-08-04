import unittest2


class TestApplication(unittest2.TestCase):

    def make_one(self):
        from jove.interfaces import Application
        class Derived(Application):
            def configure(self, config): #pragma NO COVERAGE
                pass
            def make_site(self): #pragma NO COVERAGE
                pass
        return Derived({})

    def test_settings_schema(self):
        import colander
        app = self.make_one()
        self.assertIsInstance(app.settings_schema(), colander.SchemaNode)

    def test_initial_settings(self):
        app = self.make_one()
        self.assertEqual(app.initial_settings(), {})

    def test_services(self):
        app = self.make_one()
        self.assertEqual(app.services(), [])
