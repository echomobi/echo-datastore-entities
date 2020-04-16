from echo.datastore.errors import InvalidValueError
from datetime import datetime
import pytz


class Property(object):
    """
    A class describing a typed, persisted attribute of a datastore entity
    """
    def __init__(self, default=None, required=False):
        """
        Args:
            default: The default value of the property
            required: Enforce the property value to be provided
        """
        self.default = None if default is None else self.validate(default)
        self.required = required
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        value = self.validate(value)
        current_value = instance.__datastore_entity__.get(self.name)
        if current_value != value or self.name not in instance.__datastore_entity__:
            if self.name not in instance.__changes__:
                instance.__changes__.append(self.name)
            instance.__datastore_entity__[self.name] = value

    def __get__(self, instance, owner):
        value = instance.__datastore_entity__.get(self.name)
        # Set the default value if no value is written
        if (self.default is not None) and (self.name not in instance.__datastore_entity__):
            value = self.default
        value = self.user_value(value)
        return value

    def __delete__(self, instance):
        del instance.__datastore_entity__[self.name]
        if self.name not in instance.__changes__:
            instance.__changes__.append(self.name)

    def __type_check__(self, user_value, data_types):
        """
        Check whether this value has the right data type
        Args:
            user_value: The user_value you want to confirm
            data_types: Type/Types to check against

        Returns:
            user_value: A type checked user value or the default value
        """
        if not isinstance(user_value, data_types) and user_value is not None:
            raise InvalidValueError(self, user_value)
        return user_value

    def validate(self, user_value):
        """Validates the value provided by the user and converts it to a value acceptable to the database"""
        raise NotImplementedError("A property must implement `validate` function")

    def user_value(self, value):
        """Converts the database value to a value usable by the user"""
        raise NotImplementedError("A property must implement `user_value` function")


class TextProperty(Property):
    def validate(self, user_value):
        return self.__type_check__(user_value, str)

    def user_value(self, value):
        return value


class IntegerProperty(Property):
    def validate(self, user_value):
        return self.__type_check__(user_value, int)

    def user_value(self, value):
        return value


class DateTimeProperty(Property):
    """Accepts a python datetime instance
    Notes:
        - Dates are automatically localized to UTC
    """
    def __init__(self, auto_now_add=False, required=False):
        default = datetime.now() if auto_now_add else None
        super(DateTimeProperty, self).__init__(default=default, required=required)

    def validate(self, user_value):
        user_value = self.__type_check__(user_value, datetime)
        if user_value and not user_value.tzinfo:
            user_value = pytz.utc.localize(user_value)
        return user_value

    def user_value(self, value):
        return value
