from concurrent.futures import ThreadPoolExecutor
from future import builtins
from google.cloud.datastore.client import Client


def put(entities):
    """Save entities to datastore

    Args:
        entities: An entity or a list of entities
    """
    return put_async(entities).result()


def put_async(entities):
    """Save to datastore asynchronously
    Args:
        entities: An entity or a list of entities
    Returns:
        A future object. Use future.result() to wait for or get the results if ready
    """
    if not hasattr(entities, "__iter__"):
        entities = [entities]
    return __executor().submit(__process_and_put_entities, entities)


def delete(entities):
    return delete_async(entities).result()


def delete_async(entities):
    if not hasattr(entities, "__iter__"):
        entities = [entities]
    return __executor().submit(__process_and_delete_entities, entities)


def __process_and_put_entities(entities):
    datastore_entities = []
    changed_entities = []
    for entity in entities:
        entity.pre_put()
        entity.__pre_put_check__()
        if entity.is_saved():
            continue
        datastore_entities.append(entity.__datastore_entity__)
        changed_entities.append(entity)
    if datastore_entities:
        __client__().put_multi(datastore_entities)
        for entity in changed_entities:
            entity.post_put(entity.__changes__)
            entity.__changes__ = []


def __process_and_delete_entities(entities):
    datastore_keys = []
    for entity in entities:
        entity.pre_delete()
        datastore_keys.append(entity.key())
    __client__().delete_multi(datastore_keys)


def __executor():
    if not hasattr(builtins, "__datastore_executor__"):
        setattr(builtins, "__datastore_executor__", ThreadPoolExecutor(max_workers=2))
    return getattr(builtins, "__datastore_executor__")


def __client__():
    if not hasattr(builtins, "__datastore_client__"):
        setattr(builtins, "__datastore_client__", Client())
    return getattr(builtins, "__datastore_client__")
