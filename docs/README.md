---
description: |
    API documentation for modules: echo.datastore, echo.datastore.db, echo.datastore.db_utils, echo.datastore.entity, echo.datastore.errors, echo.datastore.properties.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `echo.datastore` {#echo.datastore}





    
## Sub-modules

* [echo.datastore.db](#echo.datastore.db)
* [echo.datastore.db_utils](#echo.datastore.db_utils)
* [echo.datastore.entity](#echo.datastore.entity)
* [echo.datastore.errors](#echo.datastore.errors)
* [echo.datastore.properties](#echo.datastore.properties)






    
# Module `echo.datastore.db` {#echo.datastore.db}










    
# Module `echo.datastore.db_utils` {#echo.datastore.db_utils}







    
## Functions


    
### Function `delete` {#echo.datastore.db_utils.delete}



    
> `def delete(entities)`





    
### Function `delete_async` {#echo.datastore.db_utils.delete_async}



    
> `def delete_async(entities)`





    
### Function `put` {#echo.datastore.db_utils.put}



    
> `def put(entities)`


Save entities to datastore


###### Args

**`entities`**
:   An entity or a list of entities



    
### Function `put_async` {#echo.datastore.db_utils.put_async}



    
> `def put_async(entities)`


Save to datastore asynchronously

###### Args

**`entities`**
:   An entity or a list of entities



###### Returns

`A` `future` `object.` `Use` `future.result`() `to` `wait` `for` or `get` `the` `results` `if` `ready`
:   &nbsp;






    
# Module `echo.datastore.entity` {#echo.datastore.entity}








    
## Classes


    
### Class `Entity` {#echo.datastore.entity.Entity}



> `class Entity(**data)`


Creates a datastore document under the entity [EntityName]


#### Args

**`**data`** :&ensp;`kwargs`
:   Values for properties in the new record, e.g User(name="Bob")



#### Notes

Entities can be directly compared for equality each other e.g. entity.get(some_key) == entity.get(some_key)







    
#### Static methods


    
##### `Method get` {#echo.datastore.entity.Entity.get}



    
> `def get(key)`


Get an entity with the specified key


###### Args

**`key`**
:   A urlsafe key string or an instance of a Key



###### Returns

`An` `instance` of `the` `entity` `with` `the` `provided` `id`
:   &nbsp;


`Returns` `None` `if` `the` `id` `doesn't` `exist` `in` `the` `database`
:   &nbsp;

###### Raises

**`InvalidKeyError`**
:   Raised if the key provided is invalid for this entity



    
##### `Method get_by_id` {#echo.datastore.entity.Entity.get_by_id}



    
> `def get_by_id(entity_id)`


Get an entity with a specified ID(Integer) or Name(String).


###### Args

**`entity_id`**
:   An integer(id) or string(name) uniquely identifying the object



###### Returns

`An` `instance` of `the` `entity` `with` `the` `provided` `id`
:   &nbsp;


`Returns` `None` `if` `the` `id` `doesn't` `exist` `in` `the` `database`
:   &nbsp;



    
##### `Method query` {#echo.datastore.entity.Entity.query}



    
> `def query(limit=None, eventual=False, keys_only=False, order_by=None)`


Filter entities based on certain conditions, an empty query will return all entities


###### Args

**`limit`**
:   Maximum number of results to return, returns null by default


eventual:
    Defaults to strongly consistent (False). Setting True will use eventual consistency,
    but cannot be used inside a transaction or will raise ValueError
**`keys_only`**
:   Sets the results to include keys only


order_by:
    A list of field names to order by, add `-` to order descending
    e.g. ["name", "-age"]

###### Returns

A iterable query instance; call fetch() to get the results as a list.



    
#### Methods


    
##### Method `delete` {#echo.datastore.entity.Entity.delete}



    
> `def delete(self)`


Delete an entity from datastore


    
##### Method `is_saved` {#echo.datastore.entity.Entity.is_saved}



    
> `def is_saved(self)`


Checks if an entity has any changes since read via get or query or last put.
Always returns true for a new entity


###### Returns

**`Boolean`**
:   True if no changes have been made



    
##### Method `key` {#echo.datastore.entity.Entity.key}



    
> `def key(self)`


Generates a key for this Entity

###### Returns

`An` `instance` of `a` `key`, `convert` `to` `string` `to` `get` `a` `urlsafe` `key`
:   &nbsp;

###### Raises

**`NotSavedException`**
:   Raised if reading a key of an unsaved entity unless the ID is
    explicitly provided



    
##### Method `post_put` {#echo.datastore.entity.Entity.post_put}



    
> `def post_put(self, changes)`


Override this function to run logic after saving the entity


###### Args

**`changes`** :&ensp;`list`
:   A list of fields that have been updated during put



###### Notes

This function won't be called if there're no changes


    
##### Method `pre_delete` {#echo.datastore.entity.Entity.pre_delete}



    
> `def pre_delete(self)`


Override this function to run any logic before deleting the entity. e.g. clear cache


    
##### Method `pre_put` {#echo.datastore.entity.Entity.pre_put}



    
> `def pre_put(self)`


Override this function to run logic just before saving the entity
NB: This function won't be called if no changes were made. i.e. when self.is_saved() == True


    
##### Method `put` {#echo.datastore.entity.Entity.put}



    
> `def put(self)`


Save changes made on this entity to datastore. Won't call datastore if no changes were made


    
### Class `Key` {#echo.datastore.entity.Key}



> `class Key(*path_args, **kwargs)`


An immutable representation of a datastore Key.

**Testsetup:&ensp;key-ctor:** 
from google.cloud import datastore

project = 'my-special-pony'
client = datastore.Client(project=project)
Key = datastore.Key

parent_key = client.key('Parent', 'foo')

To create a basic key directly:

**Doctest:&ensp;key-ctor:** 
>>> Key('EntityKind', 1234, project=project)
<Key('EntityKind', 1234), project=...>
>>> Key('EntityKind', 'foo', project=project)
<Key('EntityKind', 'foo'), project=...>

Though typical usage comes via the
:meth:`~google.cloud.datastore.client.Client.key` factory:

**Doctest:&ensp;key-ctor:** 
>>> client.key('EntityKind', 1234)
<Key('EntityKind', 1234), project=...>
>>> client.key('EntityKind', 'foo')
<Key('EntityKind', 'foo'), project=...>

To create a key with a parent:

**Doctest:&ensp;key-ctor:** 
>>> client.key('Parent', 'foo', 'Child', 1234)
<Key('Parent', 'foo', 'Child', 1234), project=...>
>>> client.key('Child', 1234, parent=parent_key)
<Key('Parent', 'foo', 'Child', 1234), project=...>

To create a partial key:

**Doctest:&ensp;key-ctor:** 
>>> client.key('Parent', 'foo', 'Child')
<Key('Parent', 'foo', 'Child'), project=...>

:type path_args: tuple of string and integer
:param path_args: May represent a partial (odd length) or full (even
                  length) key path.

:param kwargs: Keyword arguments to be passed in.

Accepted keyword arguments are

* namespace (string): A namespace identifier for the key.
* project (string): The project associated with the key.
* parent (:class:`~google.cloud.datastore.key.Key`): The parent of the key.

The project argument is required unless it has been set implicitly.



    
#### Ancestors (in MRO)

* [google.cloud.datastore.key.Key](#google.cloud.datastore.key.Key)






    
### Class `Query` {#echo.datastore.entity.Query}



> `class Query(entity, keys_only=False, eventual=False, limit=None, order_by=None)`











    
#### Methods


    
##### Method `equal` {#echo.datastore.entity.Query.equal}



    
> `def equal(self, field, value)`


Equal to filter

###### Args

**`field`**
:   Field name


**`value`**
:   Value to compare



###### Returns

`Current` [`Query`](#echo.datastore.entity.Query) `Instance`
:   &nbsp;



    
##### Method `fetch` {#echo.datastore.entity.Query.fetch}



    
> `def fetch(self)`


Get Query results as a list


    
##### Method `gt` {#echo.datastore.entity.Query.gt}



    
> `def gt(self, field, value)`


Greater Than filter

###### Args

**`field`**
:   Field name


**`value`**
:   Value to compare



###### Returns

`Current` [`Query`](#echo.datastore.entity.Query) `Instance`
:   &nbsp;



    
##### Method `gte` {#echo.datastore.entity.Query.gte}



    
> `def gte(self, field, value)`


Greater Than or Equal to filter

###### Args

**`field`**
:   Field name


**`value`**
:   Value to compare



###### Returns

`Current` [`Query`](#echo.datastore.entity.Query) `Instance`
:   &nbsp;



    
##### Method `lt` {#echo.datastore.entity.Query.lt}



    
> `def lt(self, field, value)`


Less Than filter

###### Args

**`field`**
:   Field name


**`value`**
:   Value to compare



###### Returns

`Current` [`Query`](#echo.datastore.entity.Query) `Instance`
:   &nbsp;



    
##### Method `lte` {#echo.datastore.entity.Query.lte}



    
> `def lte(self, field, value)`


Less Than or Equal to filter

###### Args

**`field`**
:   Field name


**`value`**
:   Value to compare



###### Returns

`Current` [`Query`](#echo.datastore.entity.Query) `Instance`
:   &nbsp;





    
# Module `echo.datastore.errors` {#echo.datastore.errors}








    
## Classes


    
### Class `InvalidKeyError` {#echo.datastore.errors.InvalidKeyError}



> `class InvalidKeyError(entity)`


Raised when an invalid key is provided to the entity get method



    
#### Ancestors (in MRO)

* [builtins.ValueError](#builtins.ValueError)
* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `InvalidValueError` {#echo.datastore.errors.InvalidValueError}



> `class InvalidValueError(_property, value)`


Raised if the value of a property does not fit the property type



    
#### Ancestors (in MRO)

* [builtins.ValueError](#builtins.ValueError)
* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)






    
### Class `NotSavedException` {#echo.datastore.errors.NotSavedException}



> `class NotSavedException(...)`


Raised when a key of an unsaved model is accessed



    
#### Ancestors (in MRO)

* [builtins.Exception](#builtins.Exception)
* [builtins.BaseException](#builtins.BaseException)








    
# Module `echo.datastore.properties` {#echo.datastore.properties}








    
## Classes


    
### Class `DateTimeProperty` {#echo.datastore.properties.DateTimeProperty}



> `class DateTimeProperty(auto_now_add=False, required=False)`


Accepts a python datetime instance

#### Notes

- Dates are automatically localized to UTC

#### Args

**`default`**
:   The default value of the property


**`required`**
:   Enforce the property value to be provided




    
#### Ancestors (in MRO)

* [echo.datastore.properties.Property](#echo.datastore.properties.Property)






    
### Class `IntegerProperty` {#echo.datastore.properties.IntegerProperty}



> `class IntegerProperty(default=None, required=False)`


A class describing a typed, persisted attribute of a datastore entity


#### Args

**`default`**
:   The default value of the property


**`required`**
:   Enforce the property value to be provided




    
#### Ancestors (in MRO)

* [echo.datastore.properties.Property](#echo.datastore.properties.Property)






    
### Class `Property` {#echo.datastore.properties.Property}



> `class Property(default=None, required=False)`


A class describing a typed, persisted attribute of a datastore entity


#### Args

**`default`**
:   The default value of the property


**`required`**
:   Enforce the property value to be provided





    
#### Descendants

* [echo.datastore.properties.DateTimeProperty](#echo.datastore.properties.DateTimeProperty)
* [echo.datastore.properties.IntegerProperty](#echo.datastore.properties.IntegerProperty)
* [echo.datastore.properties.TextProperty](#echo.datastore.properties.TextProperty)





    
#### Methods


    
##### Method `user_value` {#echo.datastore.properties.Property.user_value}



    
> `def user_value(self, value)`


Converts the database value to a value usable by the user


    
##### Method `validate` {#echo.datastore.properties.Property.validate}



    
> `def validate(self, user_value)`


Validates the value provided by the user and converts it to a value acceptable to the database


    
### Class `TextProperty` {#echo.datastore.properties.TextProperty}



> `class TextProperty(default=None, required=False)`


A class describing a typed, persisted attribute of a datastore entity


#### Args

**`default`**
:   The default value of the property


**`required`**
:   Enforce the property value to be provided




    
#### Ancestors (in MRO)

* [echo.datastore.properties.Property](#echo.datastore.properties.Property)







-----
Generated by *pdoc* 0.7.5 (<https://pdoc3.github.io>).
