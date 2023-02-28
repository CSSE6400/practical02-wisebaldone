from todo import create_app
import unittest

class TodoTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_overrides={
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True
        })

        self.client = self.app.test_client()

    def assertDictSubset(self, expected: dict, todo: dict):
        for key, value in expected.items():
            self.assertEqual(todo[key], value)