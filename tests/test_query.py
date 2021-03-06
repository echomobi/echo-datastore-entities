import unittest
from echo.datastore import db
from google.cloud.datastore import Client, Entity as DatastoreEntity, Key


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

    def test_keys_only(self):
        i = 1
        for key in TestEntity.query(keys_only=True, limit=10, order_by=["prop2"]):
            self.assertIsInstance(key, Key)
            self.assertEqual(key.id, i)
            i += 1

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
        limit = 20
        entities = TestEntity.query(limit=limit, order_by="prop2").fetch()
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
        self.assertEqual(len(entities), 19)
        for entity in entities:
            self.assertTrue(entity.prop2 > 30)

    def test_greater_than_or_equal_to(self):
        entities = TestEntity.query().gte("prop2", 30).fetch()
        self.assertEqual(len(entities), 20)
        for entity in entities:
            self.assertTrue(entity.prop2 >= 30)

    def test_less_than(self):
        entities = TestEntity.query().lt("prop2", 20).fetch()
        self.assertEqual(len(entities), 20)
        for entity in entities:
            self.assertTrue(entity.prop2 < 20)

    def test_less_than_or_equal_to(self):
        entities = TestEntity.query().lte("prop2", 20).fetch()
        self.assertEqual(len(entities), 21)
        for entity in entities:
            self.assertTrue(entity.prop2 <= 20)

    def test_compound_query(self):
        entities = TestEntity.query().gte("prop2", 20).lt("prop2", 30).fetch()
        self.assertEqual(len(entities), 10)
        for entity in entities:
            self.assertTrue(20 <= entity.prop2 < 30)

        odd_entities = TestEntity.query().lte("prop2", 20).equal("prop1", "Odd").fetch()
        self.assertEqual(len(odd_entities), 10)
        for entity in odd_entities:
            self.assertEqual(entity.prop1, "Odd")
            self.assertTrue(entity.prop2 <= 20)
