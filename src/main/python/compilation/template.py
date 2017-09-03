# This contains the methods that edit a templeta file
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import os
import uuid

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

	# Write the file out again
	with open(filename, 'w') as file :
  		file.write(filedata)


	return filename