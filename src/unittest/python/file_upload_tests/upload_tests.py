#!/usr/bin/env python
#  Upload file tests
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more informations

import file_upload.upload as upload
import urllib
import http.client, urllib.parse
import alde
import requests
import os
import tempfile
from models import db, Application
from flask import Flask
from flask_testing import LiveServerTestCase

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
		app = alde.create_app_v1(self.SQLALCHEMY_DATABASE_URI, 0, tmp_directory)
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
		app.config['TESTING'] = self.TESTING
		db.create_all()

		# We register the upload url
		upload_prefix = alde.url_prefix_v1 + "/upload"
		app.register_blueprint(upload.upload_blueprint, url_prefix=upload_prefix)

		# We create the application and we store it in the db
		application = Application("AppName")
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
		print(response)
		self.assertEqual(response.code, 200)

	def test_upload(self):
		"""
		Verifies that the correct verification steps are performed when
		trying to upload a file via POST method
		"""

		# We verify that if the application does not exists we don't get anything
		error_message = upload.upload_application("asdf")
		self.assertEquals("Application with id: asdf does not exists in the database", error_message)

		# We verify that if no file in the payload we get an error
		params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		server_url = self.get_server_url()[7:]
		conn = http.client.HTTPConnection(server_url)
		conn.request("POST", "/api/v1/upload/1", params, headers)
		response = conn.getresponse()
		data = response.read()
		conn.close()

		self.assertEquals(b'No file specified', data)

		# Now we pass the file, not supported one... 
		outfile_path = tempfile.mkstemp(suffix='.txt')[1]
		try:
			write_lamb(outfile_path)
			files = {'file': open(outfile_path, 'rb')}
			r = requests.post(self.get_server_url() + "/api/v1/upload/1", files=files)
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
			r = requests.post(self.get_server_url() + "/api/v1/upload/1", files=files)
			self.assertEquals("file upload for app with id: 1", r.text.splitlines()[-1])
		finally:
			# NOTE: To retain the tempfile if the test fails, remove
			# the try-finally clauses
			os.remove(outfile_path)
