class InvalidValueError(ValueError):
    """Raised if the value of a property does not fit the property type"""
    def __init__(self, _property, value):
        self.property = _property
        self.value = value

    def __str__(self):
        return "%s is not a valid value for property %s of type %s" % \
               (self.value, self.property.name, type(self.property).__name__)


class NotSavedException(Exception):
    """Raised when a key of an unsaved model is accessed"""
    def __str__(self):
        return "You can't read a key of an unsaved entity"


class InvalidKeyError(ValueError):
    """Raised when an invalid key is provided to the entity get method"""
    def __init__(self, entity):
        self.entity = entity

    def __str__(self):
        return "Invalid key for entity %s" % self.entity.__entity_name__()
