from echo.datastore.errors import InvalidValueError
from datetime import datetime


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
        self.default = default
        self.required = required
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        value = self.validate(value)
        instance.__datastore_entity__[self.name] = value

    def __get__(self, instance, owner):
        value = instance.__datastore_entity__.get(self.name)
        value = self.user_value(value)
        return value

    def __type_check__(self, user_value, data_types):
        """
        Check whether this value has the right data type
        Args:
            user_value: The user_value you want to confirm
            data_types: Type/Types to check against

        Returns:
            user_value: A type checked user value or the default value
        """
        if self.required and self.default is None and user_value is None:
            raise InvalidValueError(self, user_value)
        # Assign a default value if None is provided
        if user_value is None:
            user_value = self.default

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
    def __init__(self, auto_now_add=False, required=False):
        default = datetime.now() if auto_now_add else None
        super(DateTimeProperty, self).__init__(default=default, required=required)

    def validate(self, user_value):
        return self.__type_check__(user_value, datetime)

    def user_value(self, value):
        return value
