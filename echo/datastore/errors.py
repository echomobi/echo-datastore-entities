class InvalidValueError(ValueError):
    """Raised if the value of a property does not fit the property type"""

    def __init__(self, _property, value):
        self.property = _property
        self.value = value

    def __str__(self):
        return "%s is not a valid value for property %s of type %s" % \
               (self.value, self.property.name, type(self.property).__name__)
