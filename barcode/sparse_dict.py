class SparseDict(dict):
    def __init__(self, *args, default=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default

    def __setitem__(self, key, value):
        if value == self.default:
            self.pop(key, None)
        else:
            super().__setitem__(key, value)

    def __missing__(self, key):
        return self.default
