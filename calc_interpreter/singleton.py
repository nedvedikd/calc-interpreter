class Singleton(type):
    _instances = {}

    def __call__(cls, tree):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(tree)
        instance = cls._instances[cls]
        instance.tree = tree  # update tree
        return instance

    def clear(cls):
        try:
            del Singleton._instances[cls]
        except KeyError:
            return
