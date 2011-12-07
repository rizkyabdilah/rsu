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
from cgi import parse_qs, FieldStorage

class Router(object):
    
    def __init__(self):
        self.routes = {}
        
    def add_route(self, path, method='GET'):
        regex = re.compile(path)
        
        def decorator(handler):
            def wrapper(env, resp):
                return handler(env, resp)
                
            self.routes[regex] = wrapper
            wrapper.methods = method.split(',')
            
            return wrapper
        
        return decorator
    
    def get(self, path):
        handler = None
        handler_args = {}
        
        for key in self.routes.iterkeys():
            match = key.match(path)
            if match:
                handler_args = match.groupdict()
                for k, v in handler_args.items():
                    if v is None: del handler_args[k]
                    
                handler = self.routes[key]
                break
            
        return handler, handler_args
    
    def route(self):
        def handler(env, resp):
            path = env.get('PATH_INFO')
            route, args = self.get(path)
            env['args'] = args
            
            if env.get('REQUEST_METHOD') in ('GET', 'HEAD'):
                qs = parse_qs(env.get('QUERY_STRING', ''))
                for key, value in qs.iteritems():
                    env['args'][key] = value[0]
                    
            elif env.get('REQUEST_METHOD') in ('POST', 'PUT'):
                fs = FieldStorage(env.get('wsgi.input'), environ=env, keep_blank_values=True)
                for key in fs:
                    env['args'][key] = fs.getvalue(key, '')
            
            return route(env, resp)
            
        return handler
    