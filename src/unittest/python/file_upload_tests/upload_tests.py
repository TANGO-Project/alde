#!/usr/bin/env python
#  Upload file tests
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more informations

import file_upload.upload as upload
import unittest.mock as mock
import uuid
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Application

class ApplicationMappingTest(MappingTest):
	"""
	Series of tests to validate the correct work of upload an application
	source code
	"""

	filename_uuid = uuid.uuid4()

	def test_allowed_files(self):
		"""
		Verifies that the right filenames are only used
		"""

		self.assertFalse(upload.allowed_file("asdf"))
		self.assertFalse(upload.allowed_file("asdf.tif"))
		self.assertFalse(upload.allowed_file("asdf.zip.tif"))
		self.assertTrue(upload.allowed_file("asdf.zip"))
		self.assertTrue(upload.allowed_file("asdf.zIp"))

	@mock.patch("uuid.uuid4")
	@mock.patch("flask.request")
	def test_upload(self, uuid_mock, request_mock):
		"""
		Verifies that the correct verification steps are performed when
		trying to upload a file via POST method
		"""

		# We verify that if the application does not exists we don't get anything
		error_message = upload.upload_application("asdf")
		self.assertEquals("Application with id: asdf does not exists in the database", error_message)
		uuid_mock.assert_not_called()

		# We prepare the mocks for the next test
		uuid_mock.return_value = self.filename_uuid
		#type(request_mock.return_value).files = mock.PropertyMock(return_value=None)

		# We create the application and we store it in the db
		application = Application("AppName")
		db.session.add(application)
		db.session.commit()

		message = upload.upload_application(1)
		self.assertEquals("No file specified", message)
		#print(message)
		uuid_mock.assert_called()