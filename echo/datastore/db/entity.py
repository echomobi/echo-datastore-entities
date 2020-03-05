from google.cloud.datastore import Client, Entity as DatastoreEntity, Key as DatastoreKey, Query as DatastoreQuery
import builtins


class Entity(object):
    """Creates a datastore document under the entity [EntityName]

    Args:
        **data (kwargs): Values for properties in the new record, e.g User(name="Bob")

    Attributes:
        id (str or int): Unique id identifying this record,
            if auto-generated, this is not available before `put()`
    """

    def __init__(self, **data):
        if type(self) is Entity:
            raise Exception("You must extend Entity")
        self.__id = None
        if "id" in data:
            self.__id = data.get("id")
        self.__datastore_entity__ = DatastoreEntity(key=self.key())
        for key, value in data.items():
            setattr(self, key, value)

    def key(self):
        paths = [self.__entity_name__()]
        if self.__id:
            paths.append(self.__id)
        project = Entity.__get_client__().project
        return Key(*paths, project=project)

    def put(self):
        self.post_put()
        self.pre_put()

    @classmethod
    def get(cls, key):
        if isinstance(key, str):
            key = Key.from_legacy_urlsafe(key)
        ds_entity = Entity.__get_client__().get(key=key)
        if ds_entity:
            entity = cls(id=key.id_or_name)
            entity.__datastore_entity__ = ds_entity
            return entity

    @classmethod
    def query(cls, limit=None):
        pass

    @classmethod
    def get_by_id(cls, key):
        pass

    @classmethod
    def __entity_name__(cls):
        return cls.__name__

    @staticmethod
    def __get_client__() -> Client:
        if not hasattr(builtins, "__datastore_client__"):
            setattr(builtins, "__datastore_client__", Client())
        return getattr(builtins, "__datastore_client__")

    def post_put(self):
        """Override this method if you have actions that want to run after saving the entity"""

    def pre_put(self):
        """Override this method if you have actions that want to run before saving the entity"""


class Query(object):
    def __init__(self, entity):
        self.__datastore_query: DatastoreQuery = Entity.__get_client__().query(kind=entity.__entity_name__())

    def equal(self, field, value):
        self.__datastore_query.add_filter(field, '=', value)
        return self

    def gt(self, field, value):
        self.__datastore_query.add_filter(field, '>', value)
        return self

    def gte(self, field, value):
        self.__datastore_query.add_filter(field, '>=', value)
        return self

    def lt(self, field, value):
        self.__datastore_query.add_filter(field, '<', value)
        return self

    def lte(self, field, value):
        self.__datastore_query.add_filter(field, '<=', value)
        return self


class Key(DatastoreKey):
    def __repr__(self):
        return self.to_legacy_urlsafe()

    def __str__(self):
        return self.__repr__()
