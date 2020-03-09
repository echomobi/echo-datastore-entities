import unittest
from echo.datastore import Entity
from google.cloud.datastore.client import Client


class TestEntity(unittest.TestCase):
    def test_client(self):
        self.assertIsInstance(Entity.__get_client__(), Client)
