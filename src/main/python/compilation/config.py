#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Module that parses the configuration compilation file
#

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