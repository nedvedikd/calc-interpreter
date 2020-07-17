class Singleton(type):
    _instances = {}

    def __call__(cls, parser):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(parser)
        instance = cls._instances[cls]
        instance.parser = parser  # update parser
        return instance
