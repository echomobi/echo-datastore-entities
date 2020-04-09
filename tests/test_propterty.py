import unittest
from echo.datastore import db, properties, errors
from datetime import datetime
import pytz


class TestEntity(db.Entity):
    default_property = properties.Property()
    integer_property = db.IntegerProperty()
    integer_property_with_default = db.IntegerProperty(default=10)
    integer_property_required = db.IntegerProperty(required=10)
    text_property = db.TextProperty()
    datetime_property = db.DateTimeProperty()
    auto_now_add_property = db.DateTimeProperty(auto_now_add=True)


class PropertiesTestCase(unittest.TestCase):
    def setUp(self):
        self.entity = TestEntity()

    def assertInvalidValues(self, field, *invalid_values):
        for value in invalid_values:
            self.assertRaises(errors.InvalidValueError, setattr, self.entity, field, value)

    def test_basic_property(self):
        # You shouldn't use a property without implementing it first
        self.assertRaises(NotImplementedError, setattr, self.entity, "default_property", 10)
        self.assertRaises(NotImplementedError, getattr, self.entity, "default_property")

        # Default value should be set on get
        self.assertEqual(self.entity.integer_property_with_default, 10)

    def test_integer_property(self):
        # Setting a value should update it's value in the __datastore_entity__ dict
        self.entity.integer_property = 36
        self.assertEqual(self.entity.__datastore_entity__.get("integer_property"), 36)
        # Deleting it should remove it from the dict too.
        del self.entity.integer_property
        self.assertNotIn("integer_property", self.entity.__datastore_entity__)
        self.assertInvalidValues("integer_property", "10", 10.3, {})

    def test_text_property(self):
        self.entity.text_property = "Some text"
        self.assertEqual(self.entity.__datastore_entity__.get("text_property"), "Some text")
        self.assertInvalidValues("text_property", 10, {}, [])

    def test_datetime_property(self):
        self.assertIsInstance(self.entity.auto_now_add_property, datetime)
        now = pytz.utc.localize(datetime.now())
        self.entity.datetime_property = now
        self.entity.auto_now_add_property = now
        self.assertEqual(self.entity.__datastore_entity__.get("datetime_property"), now)
        self.assertEqual(self.entity.__datastore_entity__.get("auto_now_add_property"), now)
        now_date = now.date()
        self.assertInvalidValues("datetime_property", now_date, "10th May 2019", 1232413213)
