import unittest
from echo.datastore import Entity, db
from echo.datastore.errors import NotSavedException, InvalidKeyError, InvalidValueError
from google.cloud.datastore.client import Client, Key, Entity as DatastoreEntity


class TestEntity(Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()


class TestEntityTestCase(unittest.TestCase):
    def test_client(self):
        self.assertIsInstance(Entity.__get_client__(), Client)

    def test_value_setting(self):
        entity = TestEntity()
        entity.prop1 = "Text Value"
        entity.prop2 = 1
        self.assertEqual(entity.__datastore_entity__.get("prop1"), "Text Value")
        self.assertEqual(entity.__datastore_entity__.get("prop2"), 1)

    def test_invalid_values(self):
        entity = TestEntity()
        # Test setting invalid values
        self.assertRaises(InvalidValueError, setattr, entity, "prop1", 10)  # Text property setting int
        self.assertRaises(InvalidValueError, setattr, entity, "prop2", "text")  # Int property setting Text
        self.assertRaises(InvalidValueError, setattr, entity, "prop2", 10.3)  # Int property setting Float

    def test_key_generation(self):
        entity = TestEntity()
        # You should not get a key for an unsaved entity
        self.assertRaises(NotSavedException, entity.key)

        entity = TestEntity(id=10)
        project = Entity.__get_client__().project
        expected_key = Key('TestEntity', 10, project=project)
        self.assertEqual(str(entity.key()), expected_key.to_legacy_urlsafe().decode("utf-8"))
        self.assertEqual(entity.key().id, 10)
        self.assertEqual(expected_key.id, entity.key().id)
        # TODO: Test for key generation after put

    def test_get(self):
        # Write entity via Google's API
        client = Client()
        key = client.key('TestEntity', 10)
        entity = DatastoreEntity(key)
        entity["prop1"] = "Text Value"
        entity["prop2"] = 10
        client.put(entity)

        # Read via our wrapper
        key_string = key.to_legacy_urlsafe().decode("utf-8")
        test_entity = TestEntity.get(key_string)
        self.assertEqual(str(test_entity.key()), key_string)
        self.assertEqual(test_entity.prop1, "Text Value")
        self.assertEqual(test_entity.prop2, 10)

        test_entity = TestEntity.get_by_id(10)
        self.assertEqual(str(test_entity.key()), key_string)
        # Un existing ID should just return null
        self.assertIsNone(TestEntity.get_by_id(110))

        self.assertRaises(InvalidKeyError, TestEntity.get, "INVALID_KEY")
        self.assertRaises(InvalidKeyError, TestEntity.get, 10)
        self.assertRaises(InvalidKeyError, TestEntity.get,
                          Key('AnotherEntity', 10, project=Entity.__get_client__().project))
