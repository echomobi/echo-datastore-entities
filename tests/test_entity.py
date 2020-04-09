import unittest
from datetime import datetime
from echo.datastore import Entity, db, db_utils
from echo.datastore.errors import NotSavedException, InvalidKeyError, InvalidValueError
from google.cloud.datastore.client import Client, Key, Entity as DatastoreEntity


class TestEntity(Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()
    required_property = db.DateTimeProperty(required=True)
    required_default = db.DateTimeProperty(auto_now_add=True, required=True)


class TestEntityTestCase(unittest.TestCase):
    def assertRaisesWithMessage(self, expected_exception, message, function, *args, **kwargs):
        try:
            function(*args, **kwargs)
            self.fail()
        except expected_exception as ex:
            self.assertEqual(str(ex), message)

    def test_client(self):
        self.assertIsInstance(db_utils.__client__(), Client)

    def test_entity_creation(self):
        self.assertRaisesWithMessage(Exception, "You must extend Entity", Entity, id=30)

    def test_value_setting(self):
        entity = TestEntity()
        entity.prop1 = "Text Value"
        entity.prop2 = 1
        self.assertEqual(entity.__datastore_entity__.get("prop1"), "Text Value")
        self.assertEqual(entity.__datastore_entity__.get("prop2"), 1)

    def test_invalid_values(self):
        entity = TestEntity()
        # Test setting invalid values
        message = "10 is not a valid value for property prop1 of type TextProperty"
        self.assertRaisesWithMessage(InvalidValueError, message, setattr, entity, "prop1",
                                     10)  # Text property setting int
        message = "text is not a valid value for property prop2 of type IntegerProperty"
        self.assertRaisesWithMessage(InvalidValueError, message, setattr, entity, "prop2",
                                     "text")  # Int property setting Text
        message = "10.3 is not a valid value for property prop2 of type IntegerProperty"
        self.assertRaisesWithMessage(InvalidValueError, message, setattr, entity, "prop2",
                                     10.3)  # Int property setting Float

    def test_key_generation(self):
        entity = TestEntity()
        # You should not get a key for an unsaved entity
        self.assertRaisesWithMessage(NotSavedException, "You can't read a key of an unsaved entity", entity.key)

        entity = TestEntity(id=10, required_property=datetime.now())
        project = db_utils.__client__().project
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
        message = "Invalid key for entity TestEntity"
        self.assertRaisesWithMessage(InvalidKeyError, message, TestEntity.get, "INVALID_KEY")
        self.assertRaisesWithMessage(InvalidKeyError, message, TestEntity.get, 10)
        self.assertRaisesWithMessage(InvalidKeyError, message, TestEntity.get,
                                     Key('AnotherEntity', 10, project=db_utils.__client__().project))

    def test_put(self):
        entity = TestEntity()
        self.assertFalse(entity.is_saved())
        # Test that we can't put without setting the value of a required entity
        self.assertRaisesWithMessage(ValueError, "Required field 'required_property' is not set for TestEntity",
                                     entity.put)
        # Test that we can save an entity without adding non-required values
        entity.required_property = datetime.now()
        entity.put()
        self.assertTrue(entity.is_saved())
        saved_entity = TestEntity.get(str(entity.key()))
        self.assertEqual(saved_entity.key().id, entity.key().id)
        self.assertEqual(saved_entity.key(), saved_entity.key())
        self.assertEqual(saved_entity.required_property, entity.required_property)
        # Confirm that we set the default value and it was written to datastore
        self.assertIsInstance(saved_entity.__datastore_entity__.get("required_default"), datetime)
        self.assertTrue(saved_entity.is_saved())
        # Confirm that a default value can be explicitly set as None
        saved_entity.required_property = None
        self.assertFalse(saved_entity.is_saved())
        saved_entity.put()
        self.assertIsNone(saved_entity.__datastore_entity__["required_property"])
        self.assertTrue(saved_entity.is_saved())
        # Confirm that delete deletes a value from the entity
        del saved_entity.required_property
        self.assertFalse(saved_entity.is_saved())
        self.assertRaisesWithMessage(ValueError, "Required field 'required_property' is not set for TestEntity",
                                     saved_entity.put)
