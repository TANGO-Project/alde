#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.gnu.org/licenses/agpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# HTTP Method to upload the code of an application to be compiled.
#

import os
import uuid
from flask import Blueprint, request
from models import db, Application, Executable
from flask import current_app as app

upload_blueprint = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = set(['zip'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_blueprint.route('/<app_id>', methods=['POST'])
def upload_application(app_id):

	application = db.session.query(Application).filter_by(id=app_id).first()
	upload_folder = app.config['APP_FOLDER']

	compilation_type = request.args.get('compilation_type')
	compilation_script = request.args.get('compilation_script')

	if not application:
		return "Application with id: " + str(app_id) + " does not exists in the database"
	elif not compilation_type:
		return "It is necessary to specify a compilation_type query param"
	elif not compilation_script:
		return "It is necessary to specify a compilation_script query param"
	else:
		# We define a filename
		filename_uuid = uuid.uuid4()

		if 'file' not in request.files:
			return "No file specified"
		print(request.files)
		file = request.files['file']
		
		if file.filename == '':
			return "No file specified"
		if file and allowed_file(file.filename):
			filename = str(uuid.uuid4()) + ".zip"
			file.save(os.path.join(upload_folder, filename))

			# We store the compilation/executable information in the db
			executable = Executable()
			executable.source_code_file = filename
			executable.compilation_script = compilation_script
			executable.compilation_type = compilation_type
			application.executables.append(executable)
			db.session.commit()

			return "file upload for app with id: " + str(app_id)
		else:
			return "file type not supported"