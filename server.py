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

import os
import sys
import redis
from optparse import OptionParser
from gevent.pywsgi import WSGIServer
from gevent.monkey import patch_all; patch_all()

from shorturl.lib import (router,
                          template,
                          utils)

from shorturl import shorturl

router = router.Router()
add_route = router.add_route

@add_route(r'^/(?P<short_url>[a-zA-Z0-9]+)$', 'GET')
def redirect(env, resp):
    long_url = su.get(env['args'].get('short_url'))
    
    if long_url:
        resp(
                '301 Moved Permanently',
                [
                    ('Content-Type', 'text/plain; charset=utf-8'),
                    ('Location', long_url),
                    ('X-Powered-By', 'rsu 0.1')
                ]
             )
        
        return ['301 Moved Permanently']
    else:
        resp(
                '404 Not Found',
                [
                    ('Content-Type', 'text/plain; charset=utf-8')
                ]
            )
        
        return ['404 Not Found']
    
@add_route(r'^/a/generate$', 'POST')
def generate(env, resp):
    long_url = env['args'].get('long_url')
    short_url = su.create(long_url)
    
    if short_url[0]:
        resp('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        message = 'Long URL = %s <br />Short URL = %s' % (long_url, short_url[1]) 
        return [message]
    else:
        resp('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8'), ('X-Powered-By', 'Shorten URL 0.1')])
        message = 'Failed, Internal Server Error'
        return [message]


if __name__ == '__main__':
    usage = "usage: python %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("--config-file", action="store", type="string", help="config file")
    parser.add_option("--port", action="store", type="int", help="running port")
    
    (options, args) = parser.parse_args()
    
    config_file = options.config_file
    port = options.port
    if not config_file:
        print "Config file not set, use -h for help"
        sys.exit(1)
    elif not os.path.exists(os.path.realpath(config_file)):
        print "Config file not exists or permission denied"
        sys.exit(1)
        
    if not port:
        port = 22001
    
    config = utils.parse_raw_config(config_file)
    
    host_name = config.get('core', 'host')
    domain = 'http://%s:%s' % (host_name, port)
    
    redis_host = config.get('redis', 'host')
    redis_port = config.get('redis', 'port')
    redis_db = config.get('redis', 'db')
    
    _redis_conn = redis.Redis(host=redis_host, port=int(redis_port), db=redis_db)
    
    su = shorturl.Shorturl(_redis_conn)
    
    server = WSGIServer((host_name, int(port)), router.route())
    try:
        print "running on %s %d" % (domain, os.getpid())
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
