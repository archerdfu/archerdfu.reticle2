from operator import index


class FixedSizeList(list):
    def __init__(self, *items, size=8, filler=None):
        self._size = size
        self.filler = filler
        if items:
            # If items are provided, use them up to the specified size
            initial_items = list(items[:size])
            # If fewer items are provided than the size, fill the rest with the filler
            initial_items.extend([filler] * (size - len(initial_items)))
        else:
            # If no items are provided, initialize the list with the filler
            initial_items = [filler] * size
        super().__init__(initial_items)

    def append(self, item):
        raise ValueError("Cannot append to a fixed-size list")

    def extend(self, items):
        raise ValueError("Cannot extend a fixed-size list")

    def insert(self, index, item):
        raise ValueError("Cannot insert into a fixed-size list")

    def __setitem__(self, index, value):
        if not (0 <= index < self._size):
            raise IndexError("Index out of range")
        super().__setitem__(index, value)

    def __delitem__(self, index):
        raise ValueError("Cannot delete items from a fixed-size list")

    def pop(self, index=-1):
        pop_item = self[index]
        self[index] = self.filler
        return pop_item

    def remove(self, value):
        self[index] = self.filler

    def __repr__(self):
        return f"<{self.__class__.__name__}({super().__repr__()})>"


class RestrictedDict(dict):
    """
    A dictionary that only allows predefined immutable keys and enforces
    that all values are of a specific type.
    """

    allowed_keys = {'name', 'age', 'email'}  # Example set of allowed keys
    value_type = (str, int)  # Example tuple of allowed value types

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validate initial dictionary contents
        for key, value in self.items():
            self._validate_key(key)
            self._validate_value(value)

        for key in self.allowed_keys:
            if key not in self:
                self[key] = None

    def _validate_key(self, key):
        if key not in self.allowed_keys:
            raise KeyError(f"Key '{key}' is not allowed. Allowed keys are: {self.allowed_keys}")

    def _validate_value(self, value):
        if not isinstance(value, self.value_type):
            raise TypeError(f"Value '{value}' is not of type {self.value_type}")

    def __setitem__(self, key, value):
        self._validate_key(key)
        self._validate_value(value)
        super().__setitem__(key, value)

    def update(self, m, /, **kwargs):
        for key, value in dict(m.items(), **kwargs).items():
            self._validate_key(key)
            self._validate_value(value)
        super().update(m, **kwargs)

    def pop(self, key):

        pop_item = self[key]
        self[key] = None
        return pop_item

    def __getattr__(self, name):
        if name in self.allowed_keys:
            return self[name]

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'

