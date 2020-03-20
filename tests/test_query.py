import unittest
from echo.datastore import db
from google.cloud.datastore import Client, Entity as DatastoreEntity


class TestEntity(db.Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()


class MyTestCase(unittest.TestCase):
    def setUp(self):
        client = Client()
        # Add data to the entity for querying
        for i in range(50):
            entity = DatastoreEntity(key=client.key('TestEntity', i+1))
            entity["prop1"] = "Odd" if i % 2 else "Odd"
            entity["prop2"] = i
            client.put(entity)

    def test_empty_query_returns_all_data(self):
        results = TestEntity.query().fetch()
        self.assertEqual(len(results), 50)

