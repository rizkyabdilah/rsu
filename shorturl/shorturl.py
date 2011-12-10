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
    
    db = None
    regex_url = re.compile("^(?:(?P<scheme>http|ftps?):\/\/)?(?:(?:(?P<username>[\w\.\-\+%!$&'\(\)*\+,;=]+):*(?P<password>[\w\.\-\+%!$&'\(\)*\+,;=]+))@)?(?P<host>[a-z0-9-]+(?:\.[a-z0-9-]+)*(?:\.[a-z\.]{2,6})+)(?:\:(?P<port>[0-9]+))?(?P<path>\/(?:[\w_ \/\-\.~%!\$&\'\(\)\*\+,;=:@]+)?)?(?:\?(?P<query>[\w_ \-\.~%!\$&\'\(\)\*\+,;=:@\/]*))?(?:(?P<fragment>#[\w_ \-\.~%!\$&\'\(\)\*\+,;=:@\/]*))?$")
    START_ITERATION = 130892
    #max = 2^64 - 1 - START_ITERATION
    ALPHABET = "9V6QHY31TwcemC8iNJd40Fog7LKSPafusAOZjhBWvqXklbrznyItG2ExUpRD5M"
    #ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # maksimal key dalam 1 bucket hashmap <not used>
    # di redis, yang optimal 1 bucket hashmap berisi sekitar 1000
    # <http://tumblr.com/ZElL-wBNK8Y6>
    # MAXBUCKET = 1024
        
    def __init__(self, db_object):
        if self.db is None:
            self.db = db_object
    
        if not self.db.get('iteration'):
            self.db.set('iteration', self.START_ITERATION)
    
    def valid_url(self, long_url):
        return re.match(self.regex_url, long_url) is not None
    
    def base62_encode(self, iteration):
        base = 62
        rv = ''
        while iteration:
            rem = iteration % base
            iteration /= base
            rv = self.ALPHABET[rem] + rv
        return str(rv)
    
    def base62_decode(self, value):
        iteration = len(value)
        rv = 0
        for i in range(0, iteration):
            rv += self.ALPHABET.index(value[i]) * pow(62, iteration - i - 1)
        return int(rv)
    
    def generate_key(self, long_url):
        # generate again if key already used (maybe from inject short_url)
        while True:
            self.db.increment('iteration')
            short_url = self.base62_encode(int(self.db.get('iteration')))
            if not self.short_url_exists(short_url):
                break
                
        return short_url
    
    def set_key(self, long_url, short_url):
        # set long key and short key
        return self.db.hset('long_url', long_url, short_url) and self.db.hset('short_url', short_url, long_url)
    
    def short_url_exists(self, short_url):
        return self.get(short_url) != None
    
    def long_url_exists(self, long_url):
        return self.db.hget('long_url', long_url) != None
        
    def create(self, long_url):
        short_url = self.db.hget('long_url', long_url)
        
        if short_url:
            return (True, short_url)
        
        short_url = self.generate_key(long_url)
        return (self.set_key(long_url, short_url), short_url)
    
    def inject(self, long_url, short_url):
        rv = (False, 'Failed')
        
        if self.short_url_exists(short_url):
            rv = (False, 'Failed, short_url %s already used' % short_url)
        
        if self.long_url_exists(long_url):
            rv = (False, 'Failed, long_url %s already shorten, try antother long_url' % long_url)
        
        if self.set_key(long_url, short_url):
            rv = (True, 'Success')
            
        return rv
    
    def get(self, short_url):
        return self.db.hget('short_url', short_url)

    def get_bucket_number(iteration):
        return iteration % self.MAXBUCKET
    