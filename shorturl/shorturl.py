#!/usr/bin/env python

class Shorturl(object):
    
    rds = None
    start_iteration = 130892
    #max = 9223372036854775807 - start_iteration
    
    def __init__(self, redis):
        if self.rds is None:
            self.rds = redis
    
        if not self.rds.get('increment'):
            self.rds.set('iteration', self.start_iteration)
    
    def base62_encode(self, iteration):
        #ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ALPHABET = "9V6QHY31TwcemC8iNJd40Fog7LKSPafusAOZjhBWvqXklbrznyItG2ExUpRD5M"
        base = 62
        rv = ''
        while iteration:
            rem = iteration % base
            iteration /= base
            rv = ALPHABET[rem] + rv
        return rv
    
    def generate_key(self, long_url):
        # generate again if key already used (from inject short url)
        while True:
            self.rds.incr('iteration')
            short_url = self.base62_encode(int(self.rds.get('iteration')))
            if not self.short_url_exists(short_url):
                break
                
        return short_url
    
    def set_key(self, long_url, short_url):
        # set long key and short key
        return self.rds.hset('long_url', long_url, short_url) and self.rds.hset('short_url', short_url, long_url)
    
    def short_url_exists(self, short_url):
        return self.get(short_url) != None
    
    def create(self, long_url):
        short_url = self.rds.hget('long_url', long_url)
        
        if short_url:
            return (True, short_url)
        
        short_url = self.generate_key(long_url)
        return (self.set_key(long_url, short_url), short_url)
    
    def inject(self, long_url, short_url):
        rv = (500, 'Failed')
        
        if self.short_url_exists(short_url):
            rv = (500, 'Failed, short_url already used')
        elif self.set_key(long_url, short_url):
            rv = (200, 'Success')
            
        return rv
    
    def get(self, short_url):
        return self.rds.hget('short_url', short_url)

