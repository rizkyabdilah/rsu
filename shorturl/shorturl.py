"""
This file is part of rsu.

rsu is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

rsu is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with rsu.  If not, see <http://www.gnu.org/licenses/>.
"""

import re

class Shorturl(object):
    
    rds = None
    regex_url = re.compile(r"3")
    start_iteration = 130892
    #max = 9223372036854775807 - start_iteration
    
    def __init__(self, redis):
        if self.rds is None:
            self.rds = redis
    
        if not self.rds.get('increment'):
            self.rds.set('iteration', self.start_iteration)
    
    def valid_url(self, long_url):
        pass
    
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

