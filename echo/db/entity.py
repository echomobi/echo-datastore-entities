from google.cloud.datastore import Client, Entity as DatastoreEntity
import builtins


class Entity(object):
    """Creates a datastore document under the entity [EntityName]

    Args:
        **data (kwargs): Values for properties in the new record, e.g User(name="Bob")
    """
    def __init__(self, **data):
        if type(self) is Entity:
            raise Exception("You must extend Entity")
        self.__datastore_data__ = {}

    def put(self):
        self.post_put()

        self.pre_put()

    @classmethod
    def get(cls, key):
        pass

    @classmethod
    def get_by_id(cls, key):
        pass

    @classmethod
    def __entity_name__(cls):
        return cls.__name__

    @staticmethod
    def __get_client():
        if not hasattr(builtins, "__datastore_client__"):
            setattr(builtins, "__datastore_client__", Client())
        return getattr(builtins, "__datastore_client__")

    def post_put(self):
        """Override this method if you have actions that want to run after saving the entity"""

    def pre_put(self):
        """Override this method if you have actions that want to run before saving the entity"""
