#!/usr/bin/env python
#  Upload file tests
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more informations

import file_upload.upload as upload
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Application

class ApplicationMappingTest(MappingTest):
	"""
	Series of tests to validate the correct work of upload an application
	source code
	"""

	def test_allowed_files(self):
		"""
		Verifies that the right filenames are only used
		"""

		self.assertFalse(upload.allowed_file("asdf"))
		self.assertFalse(upload.allowed_file("asdf.tif"))
		self.assertFalse(upload.allowed_file("asdf.zip.tif"))
		self.assertTrue(upload.allowed_file("asdf.zip"))
		self.assertTrue(upload.allowed_file("asdf.zIp"))

	def test_upload(self):
		"""
		Verifies that the correct verification steps are performed when
		trying to upload a file via POST method
		"""

		error_message = upload.upload_application("asdf")
		self.assertEquals("Application with id: asdf does not exists in the database", error_message)