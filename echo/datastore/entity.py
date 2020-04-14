from google.cloud.datastore import Entity as DatastoreEntity, Key as DatastoreKey
from six import string_types
from echo.datastore.errors import InvalidKeyError, NotSavedException
from echo.datastore import properties, db_utils

# Override documentation for paths in this dictionary
__pdoc__ = {}


class BaseEntityMeta(type):
    __pdoc__['BaseEntityMeta'] = False

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

    Notes:
        Entities can be directly compared for equality each other e.g.
        ```entity.get(some_key) == entity.get(some_key)```
    """
    __metaclass__ = BaseEntityMeta

    def __init__(self, **data):
        if type(self) is Entity:
            raise Exception("You must extend Entity")
        project = db_utils.__client__().project
        self.__changes__ = []
        if "__entity__" in data:
            self.__datastore_entity__ = data.get("__entity__")
            del data["__entity__"]
        elif "id" in data:
            self.__datastore_entity__ = DatastoreEntity(key=Key(self.__entity_name__(), data.get("id"), project=project))
            del data["id"]
        else:
            self.__datastore_entity__ = DatastoreEntity(key=Key(self.__entity_name__(), project=project))

        for key, value in data.items():
            setattr(self, key, value)
        self.__field_set = self.__get_field_set()

    def __get_field_set(self):
        props = []
        for key, value in self.__class__.__dict__.items():
            try:
                if issubclass(value.__class__, properties.Property):
                    props.append((key, value.required, value.default))
            except TypeError:
                pass
        return props

    def key(self):
        """Generates a key for this Entity
        Returns:
            An instance of a key, convert to string to get a urlsafe key

        Raises:
            NotSavedException: Raised if reading a key of an unsaved entity unless the ID is
                explicitly provided
        """
        if self.__datastore_entity__.key.is_partial:
            raise NotSavedException()
        return Key(*self.__datastore_entity__.key.flat_path, project=db_utils.__client__().project)

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
        ds_entity = db_utils.__client__().get(key=key)
        if ds_entity:
            entity = cls(__entity__=ds_entity)
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
        key = Key(cls.__name__, entity_id, project=db_utils.__client__().project)
        return cls.get(key)

    @classmethod
    def query(cls, limit=None, eventual=False, keys_only=False, order_by=None):
        """
        Filter entities based on certain conditions, an empty query will return all entities

        Args:
            limit: Maximum number of results to return, returns null by default
            eventual:
                Defaults to strongly consistent (False). Setting True will use eventual consistency,
                but cannot be used inside a transaction or will raise ValueError
            keys_only: Sets the results to include keys only
            order_by:
                A list of field names to order by, add `-` to order descending
                e.g. ["name", "-age"]

        Returns:
            A iterable query instance; call fetch() to get the results as a list.
        """
        return Query(cls, keys_only=keys_only, eventual=eventual, limit=limit, order_by=order_by)

    def is_saved(self):
        """Checks if an entity has any changes since read via get or query or last put.
        Always returns true for a new entity

        Returns:
            Boolean: True if no changes have been made
        """
        if self.__changes__ or self.__datastore_entity__.key.is_partial:
            return False
        return True

    def __pre_put_check__(self):
        for name, required, default in self.__field_set:
            if name not in self.__datastore_entity__:
                if default is None and required:
                    raise ValueError("Required field '%s' is not set for %s" % (name, self.__entity_name__()))
                if default is not None:
                    self.__datastore_entity__[name] = default

    def put(self):
        """Save changes made on this entity to datastore. Won't call datastore if no changes were made"""
        db_utils.put(self)

    def post_put(self, changes):
        """Override this function to run logic after saving the entity

        Args:
            changes (list): A list of fields that have been updated during put

        Notes:
            This function won't be called if there're no changes
        """

    def pre_put(self):
        """Override this function to run logic just before saving the entity
        NB: This function won't be called if no changes were made. i.e. when self.is_saved() == True
        """

    def delete(self):
        """Delete an entity from datastore"""
        db_utils.delete(self)

    def pre_delete(self):
        """Override this function to run any logic before deleting the entity. e.g. clear cache"""

    @classmethod
    def __entity_name__(cls):
        return cls.__name__

    def __eq__(self, other):
        return self.__datastore_entity__ == other.__datastore_entity__


class Query(object):
    def __init__(self, entity, keys_only=False, eventual=False, limit=None, order_by=None):
        order = []
        if isinstance(order_by, (list, tuple)):
            order = order_by
        elif isinstance(order_by, str):
            order = [order_by]
        self.__datastore_query = db_utils.__client__().query(kind=entity.__entity_name__(), order=order)
        self.entity = entity
        self.keys_only = keys_only
        if keys_only:
            self.__datastore_query.keys_only()
        self.limit = limit
        self.eventual = eventual
        self.__iterator = None

    def equal(self, field, value):
        """
        Equal to filter
        Args:
            field: Field name
            value: Value to compare

        Returns:
            Current Query Instance
        """
        self.__datastore_query.add_filter(field, '=', value)
        return self

    def gt(self, field, value):
        """
        Greater Than filter
        Args:
            field: Field name
            value: Value to compare

        Returns:
            Current Query Instance
        """
        self.__datastore_query.add_filter(field, '>', value)
        return self

    def gte(self, field, value):
        """
        Greater Than or Equal to filter
        Args:
            field: Field name
            value: Value to compare

        Returns:
            Current Query Instance
        """
        self.__datastore_query.add_filter(field, '>=', value)
        return self

    def lt(self, field, value):
        """
        Less Than filter
        Args:
            field: Field name
            value: Value to compare

        Returns:
            Current Query Instance
        """
        self.__datastore_query.add_filter(field, '<', value)
        return self

    def lte(self, field, value):
        """
        Less Than or Equal to filter
        Args:
            field: Field name
            value: Value to compare

        Returns:
            Current Query Instance
        """
        self.__datastore_query.add_filter(field, '<=', value)
        return self

    def fetch(self):
        """
        Get Query results as a list
        """
        return [entity for entity in self]

    def __process_result_item(self, result_item):
        if self.keys_only:
            # The result is a datastore entity with only a key
            return Key(result_item.kind, result_item.id, project=db_utils.__client__().project)
        entity = self.entity(__entity__=result_item)
        return entity

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__iterator:
            self.__iterator = self.__datastore_query.fetch(limit=self.limit, eventual=self.eventual).__iter__()
        return self.__process_result_item(self.__iterator.__next__())

    __pdoc__["Query.next"] = False

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
