import os
import sys
import redis
from optparse import OptionParser
from gevent.pywsgi import WSGIServer
#from gevent.monkey import patch_all; patch_all()

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
                '301 Moved Temporarily',
                [
                    ('Content-Type', 'text/html; charset=utf-8'),
                    ('Location', long_url),
                    ('X-Powered-By', 'Shorten URL 0.1')
                ]
             )
        
        return ['301 Moved Temporarily']
    else:
        resp('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
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
    
    (options, args) = parser.parse_args()
    
    config_file = options.config_file
    if not config_file:
        print "Config file not set, use -h for help"
        sys.exit(1)
    elif not os.path.exists(os.path.realpath(config_file)):
        print "Config file not exists or permission denied"
        sys.exit(1)
    
    config = utils.parse_raw_config(config_file)
    
    host_name = config.get('core', 'host')
    port = config.get('core', 'start_port')
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
