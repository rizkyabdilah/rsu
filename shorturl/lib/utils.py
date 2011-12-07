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
