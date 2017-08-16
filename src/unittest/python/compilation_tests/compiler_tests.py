# Unit tests for the compiler module
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Executable
import compilation.compiler as compiler
import compilation.config as config
import unittest.mock as mock

class CompilerTests(MappingTest):
	"""
	It tests the correct work of the module compiler
	"""

	def test_return_not_compiled_executable(self):
		"""It checks the method that returns all the no compiled executables"""

		executable_1 = Executable("source1", "script1", "type1")
		executable_2 = Executable("source2", "script2", "type2")
		executable_2.status = 'pepito'

		db.session.add(executable_1)
		db.session.add(executable_2)
		db.session.commit()

		executables = compiler.return_not_compiled_executables()

		self.assertEquals(1, len(executables))
		self.assertEquals('NOT_COMPILED', executables[0].status)
		self.assertEquals("source1", executables[0].source_code_file)

	@mock.patch("compilation.compiler.compile_singularity_pm")
	def test_compile_executables(self, mock_compiler):
		""" Test the compilation procedures """

		# Changing the config file path for the running of the test.
		config.COMPILATION_CONFIG_FILE = "./src/main/python/compilation_config.json"

		executable_1 = Executable("source1", "script1", "type1")
		executable_2 = Executable("source2", "script2", "SINGULARITY:PM")

		db.session.add(executable_1)
		db.session.add(executable_2)
		db.session.commit()

		# We perform the action
		compiler.compile_executables()

		# At the end fo the test we should have those status:
		self.assertEquals(executable_1.status, Executable.__status_error_type__)
		self.assertEquals(executable_2.status, Executable.__status_compiling__)

		# We verify the mock was called:
		mock_compiler.assert_called_with(executable_2)