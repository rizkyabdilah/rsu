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

import time
import ConfigParser

def now_localtime():
	return time.strftime("%Y/%m/%d %H:%M:%S")
	
def write_log(log, type, message):
	if type == 'info':
		log.info(message)
	elif type == 'warning':
		log.warning(message)
		
	print '[%s] %s' % (type.upper(), message)

def parse_raw_config(config_file):
	raw_config = ConfigParser.ConfigParser()
	raw_config.read(config_file)
	
	return raw_config

def parse_rule(rule_file):
	raw_rule = parse_raw_config(rule_file)
	
	rules = {}
	for sect in raw_rule.sections():
		rules[sect] = {}
		for key, value in raw_rule.items(sect):
			rules[sect][key] = value
			
	return rules
