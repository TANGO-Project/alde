#!/usr/bin/env python
#  Upload file
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more informations

import os
import uuid
from flask import Blueprint, request
from models import db, Application

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = '/tmp/apps'
ALLOWED_EXTENSIONS = set(['zip'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_blueprint.route('/<app_id>', methods=['POST'])
def upload_application(app_id):

	application = db.session.query(Application).filter_by(id=app_id).first()

	if not application:
		return "Application with id: " + str(app_id) + " does not exists in the database"
	else:
		# We define a filename
		filename_uuid = uuid.uuid4()

		if 'file' not in request.files:
	 		return "No file specified"
	# 	file = request.files['file']
	# 	# if user does not select file, browser also
	# 	# submit a empty part without filename
	# 	if file.filename == '':
	# 		#flash('No selected file')
	# 		return "No file specified"
	# 	if file and allowed_file(file.filename):
	# 		filename = file.filename
	# 		file.save(os.path.join(UPLOAD_FOLDER, filename))
	# 		return app_id