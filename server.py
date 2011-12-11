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
                          response,
                          utils)
from shorturl.drivers import (rsukyoto, rsuredis)
from shorturl import shorturl

router = router.Router()
add_route = router.add_route

@add_route(r'^/$', 'GET')
def home(env, resp):
    body = """
    <html>
        <head>
            <title>MindTalk Shorturl</title>
        </head>
        <body>
            <form action="/action/generate" method="post">
                <p>
                    <label desc="Long URL">Long URL</label>
                    <input type="text" name="long_url" value="" />
                </p>
                <p>
                    <input type="submit" value="Generate" />
                </p>
            </form>
            <form action="/action/inject" method="post">
                <p>
                    <label desc="Long URL">Long URL</label>
                    <input type="text" name="long_url" value="" />
                </p>
                <p>
                    <label desc="Short URL">Short URL</label>
                    <input type="text" name="short_url" value="" />
                </p>
                <p>
                    <input type="submit" value="Inject" />
                </p>
            </form>
        </body>
    </html>
    """
    
    return response.send_response(resp,
                                  status='200 Ok',
                                  body=body,
                                  content_type='text/html; charset=utf-8')

@add_route(r'^/(?P<short_url>[a-zA-Z0-9]+)$', 'GET')
def redirect(env, resp):
    long_url = su.get(env['args'].get('short_url'))
    
    if long_url:
        return response.send_response(resp,
                                      status='301 Moved Permanently',
                                      body='301 Moved Permanently',
                                      location=long_url,
                                      content_type='text/plain; charset=utf-8')
    else:
        return response.send_response(resp,
                                      status='404 Not Found',
                                      body='404 Not Found',
                                      content_type='text/plain; charset=utf-8')
    
@add_route(r'^/action/generate$', 'POST')
def generate(env, resp):
    long_url = env['args'].get('long_url')
    
    if not long_url.startswith("http"):
        long_url = "http://%s" % long_url
    
    if not su.valid_url(long_url) or long_url.startswith(domain):
        message = 'URL %s is not valid' % (long_url) 
        return response.send_response(resp,
                                      status='500 Internal Server Error',
                                      body=message)
    
    success, short_url = su.create(long_url)
    
    if success:
        message = """
        Long URL = {long_url} <br />
        Short URL = <a href="/{short_url}">{domain}/{short_url}</a>
        """.format(long_url=long_url, domain=domain, short_url=short_url) 
        return response.send_response(resp,
                                      status='200 Ok',
                                      body=message)
    else:
        return response.send_response(resp,
                                      status='500 Internal Server Error',
                                      body='Failed, Internal Server Error')


@add_route(r'^/action/inject$', 'POST')
def inject(env, resp):
    short_url = env['args'].get('short_url')
    long_url = env['args'].get('long_url')
    
    if not long_url.startswith("http"):
        long_url = "http://%s" % long_url
    
    if not su.valid_url(long_url) or long_url.startswith(domain):
        return response.send_response(resp,
                                      status='500 Internal Server Error',
                                      body='URL %s in not valid' % long_url)
    
    success, message = su.inject(long_url, short_url)
    
    if success:
        message = """
        Long URL = {long_url} <br />
        Short URL = <a href="/{short_url}">{domain}/{short_url}</a>
        """.format(long_url=long_url, domain=domain, short_url=short_url) 
        return response.send_response(resp,
                                      status='200 Ok',
                                      body=message)
    else:
        return response.send_response(resp,
                                      status='500 Internal Server Error',
                                      body=message)


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
    
    domain = 'http://%s' % host_name
    
    if config.get('core', 'pdb') == 'redis':
        redis_host = config.get('redis', 'host')
        redis_port = config.get('redis', 'port')
        redis_db = config.get('redis', 'db')
        db = rsuredis.ShorturlDBDriver(host=redis_host, port=int(redis_port), db=redis_db)
    elif config.get('core', 'pdb') == 'kyoto':
        kyoto_db = config.get('kyoto', 'filename')
        db = rsukyoto.ShorturlDBDriver(kyoto_db)
    else:
        print "pdb not set"
        sys.exit(1)
    
    su = shorturl.Shorturl(db)
    
    server = WSGIServer((host_name, int(port)), router.route())
    try:
        print "running on %s port port %d pid %d" % (domain, port, os.getpid())
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
