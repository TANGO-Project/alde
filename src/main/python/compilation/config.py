# Parses the compilation configuration methods
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import json

COMPILATION_CONFIG_FILE = 'compilation_config.json'

def find_compilation_config(requested_type):
	"""
	This function will look at the internal compilation config inventory and look
	for the compilation config with the same "type" field and return the array
	"""

	with open(COMPILATION_CONFIG_FILE) as data_file:
		compilation_configs = json.load(data_file)

	compilation_config = next((compilation_config for compilation_config in compilation_configs if compilation_config['type'] == requested_type), None)

	return compilation_config