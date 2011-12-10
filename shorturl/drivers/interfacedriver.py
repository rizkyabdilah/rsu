from abc import (ABCMeta,
                 abstractmethod,
                 abstractproperty)

class InterfaceDriver(object):
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def db(self):
        pass
    
    @abstractmethod
    def __init__(self, **kwargs):
        pass
    
    @abstractmethod
    def increment(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def hset(self, bucket, key, value):
        pass

    @abstractmethod
    def hget(self, bucket, key):
        pass
    