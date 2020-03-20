import unittest
from echo.datastore import db
from google.cloud.datastore import Client, Entity as DatastoreEntity
from random import randint


class TestEntity(db.Entity):
    prop1 = db.TextProperty()
    prop2 = db.IntegerProperty()


class QueryTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        # Add data to the entity for querying
        for i in range(50):
            entity = DatastoreEntity(key=self.client.key('TestEntity', i + 1))
            entity["prop1"] = "Odd" if i % 2 else "Even"
            entity["prop2"] = i
            self.client.put(entity)

    def test_empty_query_returns_all_data(self):
        results = TestEntity.query().fetch()
        self.assertEqual(len(results), 50)

    def test_reverse_order(self):
        count = 0
        for entity in TestEntity.query(order_by=["-prop2"]):
            i = 50 - count - 1
            expected_key = self.client.key('TestEntity', i + 1).to_legacy_urlsafe().decode("utf-8")
            self.assertEqual(str(entity.key()), expected_key)
            self.assertEqual("Odd" if i % 2 else "Even", entity.prop1)
            self.assertEqual(i, entity.prop2)
            count += 1

    def test_order_and_limit(self):
        limit = randint(2, 20)
        entities = TestEntity.query(limit=limit, order_by=["prop2"]).fetch()
        self.assertEqual(len(entities), limit)
        for i in range(limit):
            self.assertEqual(str(entities[i].key()),
                             self.client.key('TestEntity', i + 1).to_legacy_urlsafe().decode("utf-8"))

    def test_equal_to_queries(self):
        odd_entities = TestEntity.query().equal("prop1", "Odd").fetch()
        self.assertEqual(len(odd_entities), 25)
        self.assertTrue(all([entity.prop1 == "Odd" for entity in odd_entities]))
        even_entities = TestEntity.query().equal("prop1", "Even").fetch()
        self.assertEqual(len(even_entities), 25)
        self.assertTrue(all([entity.prop1 == "Even" for entity in even_entities]))

    def test_greater_than(self):
        entities = TestEntity.query().gt("prop2", 30).fetch()
        