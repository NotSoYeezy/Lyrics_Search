class PositiveInteger:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"`{self.name}` must be a positive integer.")
        instance.__dict__[self.name] = value


class NonEmptyString:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"`{self.name}` must be a non-empty string.")
        instance.__dict__[self.name] = value
