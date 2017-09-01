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
import os
from uuid import UUID

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

	@mock.patch("compilation.compiler.upload_zip_file_application")
	@mock.patch("compilation.compiler.create_random_folder")
	def test_compile_singularity_pm(self, mock_random_folder, mock_upload_zip):
		""" Test that the right workflow is managed to create a container """

		config.COMPILATION_CONFIG_FILE = "./src/main/python/compilation_config.json"

		mock_random_folder.return_value = 'dest_folder'

		executable = Executable('test.zip', 'xxxx', 'xxxx')
		
		compiler.compile_singularity_pm(executable) # TODO Create a executable when the method evolvers.

		# We verify that a random folder was created
		mock_random_folder.assert_called_with('ubuntu@localhost:2222')
		mock_upload_zip.assert_called_with(executable, 'ubuntu@localhost:2222', 'dest_folder')

	@mock.patch("compilation.compiler.shell.execute_command")
	def test_unzip_src(self, mock_shell_execute):
		"""
		It verifies the workflow of unziping the zip file
		"""

		executable = Executable('test.zip', 'xxxx', 'xxxx')

		compiler.unzip_src(executable, 'asd@asdf.com', '/home/pepito')

		zip_file = os.path.join('/home/pepito', 'test.zip')

		mock_shell_execute.assert_called_with('unzip', 'asd@asdf.com', [ zip_file ])

	@mock.patch("compilation.compiler.shell.execute_command")
	def test_create_random_folder(self, mock_shell_excute):
		""" Test the creation of a random folder in a server """

		destination_folder = compiler.create_random_folder('server@xxxx:2222')

		try:
			val = UUID(destination_folder, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + destination_folder)

		mock_shell_excute.assert_called_with("mkdir", "server@xxxx:2222", [ destination_folder ])

	@mock.patch('compilation.compiler.shell.scp_file')
	@mock.patch('compilation.compiler.app')
	def test_upload_zip_file_application(self, mock_app, mock_scp):
		""" 
		Test the function of uploading a zip file of the application 
		to the selected testbed in an specific folder
		"""

		# We configure the variable of the mock
		mock_app.config = {'APP_FOLDER': '/tmp'}

		executable = Executable('test.zip', 'xxxx', 'xxxx')

		compiler.upload_zip_file_application(executable, 'asd@asdf.com', 'dest_folder')

		mock_scp.assert_called_with(os.path.join('/tmp', 'test.zip'), 'asd@asdf.com', './dest_folder')
