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
# Method that updats the template compilation information
#

import os
import uuid
import logging

_build_command = "{#BUILD_COMMAND#}"
_folder_location = "{#FOLDER_LOCATION#}"
_app_foler = "{#APP_FOLDER#}"
upload_folder = '/tmp' # TODO fix this ugly... ugly code

def update_template(template, build_command, folder_location='/home/tango', app_folder='application'):
	"""
	It updates a template changing the following variables:
	- build_command
	- folder_location
	- app_folder
	"""

	logging.info('Creating singulartiy template using file: %s', template)

	# Read in the file
	with open(template, 'r') as file :
		filedata = file.read()

	# Replace the target string
	filedata = filedata.replace(_build_command, build_command)
	filedata = filedata.replace(_folder_location, folder_location)
	filedata = filedata.replace(_app_foler, app_folder)	

	# We generate an uuid filename

	filename_uuid = uuid.uuid4()
	filename = str(filename_uuid) + ".def"
	filename = os.path.join(upload_folder, filename)

	logging.info('Template generated on: %s', filename)

	# Write the file out again
	with open(filename, 'w') as file :
  		file.write(filedata)


	return filename