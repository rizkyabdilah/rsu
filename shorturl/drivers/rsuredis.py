from interfacedriver import InterfaceDriver

import redis
import sys

class ShorturlDBDriver(InterfaceDriver):
    
    db = None
    
    def __init__(self, **kwargs):
        self.db = redis.StrictRedis(**kwargs)
        if not self.db:
            # redis didn't tell if fail connection, from here, I don't know what todo
            sys.exit(2)
    
    def increment(self, key):
        return self.db.incr(key)
    
    def set(self, key, value):
        return self.db.set(key, value)
        
    def get(self, key):
        return self.db.get(key)
    
    def hset(self, bucket, key, value):
        return self.db.hset(bucket, key, value)
        
    def hget(self, bucket, key):
        return self.db.hget(bucket, key)
