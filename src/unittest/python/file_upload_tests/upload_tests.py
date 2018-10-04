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
# Unit tests that updates that checks the upload of the source code. 
#

import file_upload.upload as upload
import urllib
import alde
import requests
import os
import tempfile
import json
from models import db, Application
from flask import Flask
from flask_testing import LiveServerTestCase
from uuid import UUID

def write_lamb(outfile_path):
    with open(outfile_path, 'w') as outfile:
        outfile.write("Mary had a little lamb.\n")

class ApplicationMappingTest(LiveServerTestCase):
	"""
	Series of tests to validate the correct work of upload an application
	source code
	"""

	SQLALCHEMY_DATABASE_URI = "sqlite://"
	TESTING = True

	def create_app(self):
		"""
		It initializes flask_testing
		"""
		tmp_directory = tempfile.mkdtemp()
		app = alde.create_app_v1(self.SQLALCHEMY_DATABASE_URI, 
		                         0, 
								 tmp_directory, 
								 tmp_directory,
								 ['APP_TYPE'],
								 None,
								 None)
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
		app.config['TESTING'] = self.TESTING
		db.create_all()

		# We register the upload url
		upload_prefix = alde.url_prefix_v1 + "/upload"
		app.register_blueprint(upload.upload_blueprint, url_prefix=upload_prefix)

		# We create the application and we store it in the db
		application = Application()
		application.name = "AppName"
		db.session.add(application)
		db.session.commit()

		return app

	def test_allowed_files(self):
		"""
		Verifies that the right filenames are only used
		"""

		self.assertFalse(upload.allowed_file("asdf"))
		self.assertFalse(upload.allowed_file("asdf.tif"))
		self.assertFalse(upload.allowed_file("asdf.zip.tif"))
		self.assertTrue(upload.allowed_file("asdf.zip"))
		self.assertTrue(upload.allowed_file("asdf.zIp"))

	def test_server_is_up_and_running(self):
		response = urllib.request.urlopen(self.get_server_url() + "/api/v1/testbeds")
		self.assertEqual(response.code, 200)

	def test_upload(self):
		"""
		Verifies that the correct verification steps are performed when
		trying to upload a file via POST method
		"""

		# We verify that if the application does not exists we don't get anything
		error_message = upload.upload_application("asdf")
		self.assertEquals("Application with id: asdf does not exists in the database", error_message)

		# We miss executable_type param
		r = requests.post(self.get_server_url() + "/api/v1/upload/1")
		self.assertEquals("It is necessary to specify a compilation_type query param", r.text.splitlines()[-1])

		# We miss compilation_script param
		params = { 'compilation_type': '1111' }
		r = requests.post(self.get_server_url() + "/api/v1/upload/1", params=params)
		self.assertEquals("It is necessary to specify a compilation_script query param", r.text.splitlines()[-1])

		# We don't pass a file
		params = { 'compilation_type': '1111', 'compilation_script': 'issue'}
		r = requests.post(self.get_server_url() + "/api/v1/upload/1", params=params)
		self.assertEquals("No file specified", r.text.splitlines()[-1])

		# Now we pass the file, not supported one... 
		outfile_path = tempfile.mkstemp(suffix='.txt')[1]
		try:
			write_lamb(outfile_path)
			files = {'file': open(outfile_path, 'rb')}
			r = requests.post(self.get_server_url() + "/api/v1/upload/1", params=params, files=files)
			self.assertEquals("file type not supported", r.text.splitlines()[-1])
		finally:
			# NOTE: To retain the tempfile if the test fails, remove
			# the try-finally clauses
			os.remove(outfile_path)

		# Now we pass the file supported 
		outfile_path = tempfile.mkstemp(suffix='.zip')[1]
		try:
			write_lamb(outfile_path)
			files = {'file': open(outfile_path, 'rb')}
			r = requests.post(self.get_server_url() + "/api/v1/upload/1", params=params, files=files)
			self.assertEquals("file upload for app with id: 1", r.text.splitlines()[-1])
		finally:
			# NOTE: To retain the tempfile if the test fails, remove
			# the try-finally clauses
			os.remove(outfile_path)

		r = requests.get(self.get_server_url() + "/api/v1/applications/1")
		application = json.loads(r.text)
		self.assertEquals(1, len(application['executables']))
		self.assertEquals('1111', application['executables'][0]['compilation_type'])
		self.assertEquals('issue', application['executables'][0]['compilation_script'])
		filename = application['executables'][0]['source_code_file'][:-4]

		try:
			val = UUID(filename, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + filename)