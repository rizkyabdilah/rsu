from interfacedriver import InterfaceDriver

import kyotocabinet
import sys

class ShorturlDBDriver(InterfaceDriver):
    
    db = None
    
    def __init__(self, kyoto_db):
        self.db = kyotocabinet.DB()
        if not self.db.open(kyoto_db, kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE):
            print "cannot open db"
            sys.exit(2)
    
    def increment(self, key):
        return self.db.increment(key, 1)
    
    def set(self, key, value):
        return self.db.set(key, value)
        
    def get(self, key):
        return self.db.get(key)
    
    def hset(self, bucket, key, value):
        return self.db.set(bucket + "::" + key, value)
        
    def hget(self, bucket, key):
        return self.db.hget(bucket + "::" + key)
