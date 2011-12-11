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
__default__ = {
    'content_type': 'text/html; charset=utf-8',
    'X-Powered-By': 'rsu 0.1',
    'connection': 'close',
    'body': 'Ok',
    'status': '200 Ok'
}

def get_args(key, kwargs):
    global __default__
    return kwargs.get(key, None) or __default__.get(key)

def send_response(response, **kwargs):
    global __default__
    
    headers = [
                ('Content-Type', get_args('content_type', kwargs)),
                ('X-Powered-By', __default__.get('X-Powered-By'))
            ]
    
    location = kwargs.get('location', None)
    if location:
        headers.append(('Location', location))
    
    response(
                kwargs.get('status', None) or __default__.get('status'),
                headers
            )
    
    return [get_args('body', kwargs)]
    
