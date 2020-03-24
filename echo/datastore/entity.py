from google.cloud.datastore import Client, Entity as DatastoreEntity, Key as DatastoreKey
from six import string_types
from future import builtins
from echo.datastore.errors import InvalidKeyError, NotSavedException
from echo.datastore import properties


class BaseEntityMeta(type):
    # Needed to support setting property names on python2
    def __new__(mcls, name, bases, attrs):
        cls = super(BaseEntityMeta, mcls).__new__(mcls, name, bases, attrs)
        for attr, obj in attrs.items():
            if isinstance(obj, properties.Property):
                obj.__set_name__(cls, attr)
        return cls


class Entity(object):
    """Creates a datastore document under the entity [EntityName]

    Args:
        **data (kwargs): Values for properties in the new record, e.g User(name="Bob")

    Attributes:
        id (str or int): Unique id identifying this record,
            if auto-generated, this is not available before `put()`
    """
    __metaclass__ = BaseEntityMeta

    def __init__(self, **data):
        if type(self) is Entity:
            raise Exception("You must extend Entity")
        self.__id = None
        if "id" in data:
            self.__id = data.get("id")
        self.__datastore_entity__ = DatastoreEntity(key=self.key(partial=True))
        for key, value in data.items():
            setattr(self, key, value)

    def key(self, partial=False):
        """Generates a key for this Entity
        Args:
            partial: Returns a partial key if an ID doesn't exist

        Returns:
            An instance of a key, convert to string to get a urlsafe key

        Raises:
            NotSavedException: Raised if reading a key of an unsaved entity unless partial is true or the ID is
            explicitly provided
        """
        paths = [self.__entity_name__()]
        if not self.__id and not partial:
            raise NotSavedException()
        if self.__id:
            paths.append(self.__id)
        project = Entity.__get_client__().project
        return Key(*paths, project=project)

    def put(self):
        self.post_put()
        self.pre_put()

    @classmethod
    def get(cls, key):
        """
        Get an entity with the specified key

        Args:
            key: A urlsafe key string or an instance of a Key

        Returns:
            An instance of the entity with the provided id

            Returns None if the id doesn't exist in the database

        Raises:
            InvalidKeyError: Raised if the key provided is invalid for this entity
        """
        if isinstance(key, string_types):
            try:
                key = Key.from_legacy_urlsafe(key)
            except Exception:
                raise InvalidKeyError(cls)

        if not isinstance(key, Key) or cls.__entity_name__() != key.kind:
            raise InvalidKeyError(cls)
        ds_entity = Entity.__get_client__().get(key=key)
        if ds_entity:
            entity = cls(id=key.id_or_name)
            entity.__datastore_entity__ = ds_entity
            return entity

    @classmethod
    def get_by_id(cls, entity_id):
        """
        Get an entity with a specified ID(Integer) or Name(String).

        Args:
            entity_id: An integer(id) or string(name) uniquely identifying the object

        Returns:
            An instance of the entity with the provided id

            Returns None if the id doesn't exist in the database
        """
        key = Key(cls.__name__, entity_id, project=cls.__get_client__().project)
        return cls.get(key)

    @classmethod
    def query(cls, limit=None, eventual=False, keys_only=False, order_by=None):
        return Query(cls, keys_only=keys_only, eventual=eventual, limit=limit, order_by=order_by)

    @classmethod
    def __entity_name__(cls):
        return cls.__name__

    @staticmethod
    def __get_client__():
        if not hasattr(builtins, "__datastore_client__"):
            setattr(builtins, "__datastore_client__", Client())
        return getattr(builtins, "__datastore_client__")

    def post_put(self):
        """Override this method if you have actions that want to run after saving the entity"""

    def pre_put(self):
        """Override this method if you have actions that want to run before saving the entity"""


class Query(object):
    def __init__(self, entity, keys_only=False, eventual=False, limit=None, order_by=None):
        order = []
        if isinstance(order_by, (list, tuple)):
            order = order_by
        elif isinstance(order_by, str):
            order = [str]
        self.__datastore_query = Entity.__get_client__().query(kind=entity.__entity_name__(), order=order)
        self.entity = entity
        self.keys_only = keys_only
        if keys_only:
            self.__datastore_query.keys_only()
        self.limit = limit
        self.eventual = eventual
        self.__iterator = None

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

    def fetch(self):
        return [entity for entity in self]

    def __process_result_item(self, result_item):
        if self.keys_only:
            return Key.from_legacy_urlsafe(result_item.to_legacy_urlsafe())  # Return customized key
        entity = self.entity(id=result_item.id)
        entity.__datastore_entity__ = result_item
        return entity

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__iterator:
            self.__iterator = self.__datastore_query.fetch(limit=self.limit, eventual=self.eventual).__iter__()
        return self.__process_result_item(self.__iterator.__next__())

    def next(self):
        # Support python2 iterators
        if not self.__iterator:
            self.__iterator = self.__datastore_query.fetch(limit=self.limit, eventual=self.eventual).__iter__()
        return self.__process_result_item(self.__iterator.next())


class Key(DatastoreKey):
    def __repr__(self):
        return self.to_legacy_urlsafe().decode('utf-8')

    def __str__(self):
        return self.__repr__()
