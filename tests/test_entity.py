import unittest
from echo.datastore import Entity, db
from echo.datastore import errors
from google.cloud.datastore.client import Client, Key


class TestEntity(Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()


class TestEntityTestCase(unittest.TestCase, Entity):
    def test_client(self):
        self.assertIsInstance(Entity.__get_client__(), Client)

    def test_value_setting(self):
        entity = TestEntity()
        entity.prop1 = "Text Value"
        entity.prop2 = 1
        self.assertEqual(entity.__datastore_entity__.get("prop1"), "Text Value")
        self.assertEqual(entity.__datastore_entity__.get("prop2"), 1)

    def test_key_generation(self):
        entity = TestEntity()
        # You should not get a key for an unsaved entity
        self.assertRaises(errors.NotSavedException, entity.key)

        entity = TestEntity(id=10)
        project = Entity.__get_client__().project
        expected_key = Key('TestEntity', 10, project=project)
        self.assertEqual(str(entity.key()), expected_key.to_legacy_urlsafe().decode("utf-8"))
        self.assertEqual(entity.key().id, 10)
        self.assertEqual(expected_key.id, entity.key().id)
        # TODO: Test for key generation after put
