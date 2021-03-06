import unittest
from datetime import datetime
from echo.datastore import Entity, db, db_utils
from echo.datastore.errors import NotSavedException, InvalidKeyError, InvalidValueError
from google.cloud.datastore.client import Client, Key, Entity as DatastoreEntity
from mock import patch, call


class TestEntity(Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()
    required_property = db.DateTimeProperty(required=True)
    required_default = db.DateTimeProperty(auto_now_add=True, required=True)
    class_prop = None


class TestEntityTestCase(unittest.TestCase):
    def tearDown(self):
        db_utils.delete(TestEntity.query())

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

    def test_entity_comparison(self):
        entity = TestEntity(required_property=None)
        self.assertRaises(NotSavedException, entity.delete)  # You can't delete an unsaved entity
        entity.put()
        key = str(entity.key())
        saved_entity = TestEntity.get(key)
        self.assertEqual(entity, saved_entity)
        saved_entity.prop1 = "Text values"
        self.assertNotEqual(saved_entity, entity)
        entity.prop1 = "Text values"
        self.assertEqual(saved_entity, entity)
        # Compare entities with different keys but equal values
        separate_entity = TestEntity(required_property=entity.required_property,
                                     required_default=entity.required_default, prop1=entity.prop1, prop2=entity.prop2)
        self.assertNotEqual(entity, separate_entity)
        separate_entity.put()
        self.assertNotEqual(saved_entity, separate_entity)
        self.assertEqual(separate_entity, TestEntity.get(separate_entity.key()))

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
        self.assertEqual(saved_entity, entity)
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

    @patch("google.cloud.datastore.client.Client.put_multi")
    @patch("echo.datastore.entity.Entity.post_put")
    @patch("echo.datastore.entity.Entity.pre_put")
    def test_put_utils(self, pre_put_mock, post_put_mock, put_multi_mock):
        entities = [TestEntity(id=i, required_property=None) for i in range(1, 11)]
        # We shouldn't call pre-pu or post put on creation
        entities[0].put()
        pre_put_mock.assert_called_once()
        put_multi_mock.assert_called_once_with([entities[0].__datastore_entity__])
        post_put_mock.assert_called_once()
        entities[0].put()
        self.assertEqual(pre_put_mock.call_count, 2)
        put_multi_mock.assert_called_once()
        post_put_mock.assert_called_once()
        # We don't put already saved items
        post_put_mock.reset_mock()
        pre_put_mock.reset_mock()
        put_multi_mock.reset_mock()
        db_utils.put(entities)
        self.assertEqual(pre_put_mock.call_count, 10)
        self.assertEqual(post_put_mock.call_count, 9)
        put_multi_mock.assert_called_once_with([e.__datastore_entity__ for e in entities[1:]])
        # We should only put changed items
        entities[3].required_property = datetime.now()
        entities[3].prop2 = 10
        entities[7].prop1 = "Some text"
        entities[9].required_default = None
        post_put_mock.reset_mock()
        pre_put_mock.reset_mock()
        put_multi_mock.reset_mock()
        db_utils.put(entities)
        self.assertEqual(pre_put_mock.call_count, 10)
        put_multi_mock.assert_called_once_with([e.__datastore_entity__ for e in [entities[3], entities[7], entities[9]]])
        post_put_mock.assert_has_calls([
            call(["required_property", "prop2"]),
            call(["prop1"]),
            call(["required_default"])
        ])

    def test_delete(self):
        entity = TestEntity(required_property=None)
        self.assertRaises(NotSavedException, entity.delete)  # You can't delete an unsaved entity
        entity.put()
        key = str(entity.key())
        saved_entity = TestEntity.get(key)
        self.assertEqual(entity, saved_entity)
        saved_entity.delete()
        self.assertIsNone(TestEntity.get(key))
        entities = [TestEntity(id=i, required_property=None) for i in range(1, 11)]
        db.put(entities)
        keys = [str(entity.key()) for entity in entities]
        self.assertEqual(entities, [TestEntity.get(key) for key in keys])
        db.delete(entities)
        for key in keys:
            self.assertIsNone(TestEntity.get(key))
