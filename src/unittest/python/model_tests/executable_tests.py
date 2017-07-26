# Executable represenation of an application inside ALDE
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from models import Executable

class ExecutableTest(unittest.TestCase):
	"""
	Unit tests for the class Executable
	"""

	def test_initialization_executable(self):
		"""Test the initialization of the object"""

		executable = Executable("source", "script", "type")

		self.assertEquals("source", executable.source_code_file)
		self.assertEquals("script", executable.compilation_script)
		self.assertEquals("type", executable.compilation_type)
		self.assertEquals("NOT_COMPILED", executable.status)