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
from unittest.mock import ANY, call
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
		config.COMPILATION_CONFIG_FILE = "compilation_config.json"

		executable_1 = Executable("source1", "script1", "type1")
		executable_2 = Executable("source2", "script2", "SINGULARITY:PM")

		db.session.add(executable_1)
		db.session.add(executable_2)
		db.session.commit()

		# We perform the action
		compiler.compile_executables('asdf')

		# At the end fo the test we should have those status:
		self.assertEquals(executable_1.status, Executable.__status_error_type__)
		self.assertEquals(executable_2.status, Executable.__status_compiling__)

		# We verify the mock was called:
		mock_compiler.assert_called_with(executable_2, 'asdf')

	@mock.patch('compilation.compiler.build_singularity_container')
	@mock.patch('compilation.compiler.create_singularity_image')
	@mock.patch('compilation.compiler.create_singularity_template')
	@mock.patch("compilation.compiler.unzip_src")
	@mock.patch("compilation.compiler.upload_zip_file_application")
	@mock.patch("compilation.compiler.create_random_folder")
	def test_compile_singularity_pm(self, 
									mock_random_folder, 
									mock_upload_zip,
									mock_unzip_src,
									mock_create_sing_template,
									mock_image, 
									mock_build):
		""" Test that the right workflow is managed to create a container """

		config.COMPILATION_CONFIG_FILE = "compilation_config.json"
		configuration = config.find_compilation_config('SINGULARITY:PM')

		mock_random_folder.return_value = 'dest_folder'
		mock_create_sing_template.return_value = 'template.def'
		mock_build.return_value = '/tmp/image.img'

		executable = Executable("test.zip", "xxxx", "xxxx")
		db.session.add(executable)
		db.session.commit()
		
		compiler.compile_singularity_pm(executable, 'asdf') # TODO Create a executable when the method evolvers.

		# We verify that a random folder was created
		mock_random_folder.assert_called_with('ubuntu@localhost:2222')
		# We verfiy that the src file is uploaded to the random folder
		mock_upload_zip.assert_called_with(executable, 'ubuntu@localhost:2222', 'dest_folder', 'asdf')
		# We verify that the src file is uncrompress
		mock_unzip_src.assert_called_with(executable, 'ubuntu@localhost:2222', 'dest_folder')
		# We verify that the creation of the template is done
		mock_create_sing_template.assert_called_with(configuration, executable, 'ubuntu@localhost:2222', 'dest_folder')
		# We verify that the image was created
		mock_image.assert_called_with(configuration, 'ubuntu@localhost:2222', 'singularity_pm.img')
		# We verify that the container was build
		mock_build.assert_called_with('ubuntu@localhost:2222', 'template.def', 'singularity_pm.img', 'asdf', become=True)

		executable = db.session.query(Executable).filter_by(status=Executable. __status_compiled__).first()

		self.assertEquals('test.zip', executable.source_code_file)
		self.assertEquals('COMPILED', executable.status)
		self.assertEquals('/tmp/image.img', executable.singularity_image_file)

	@mock.patch('compilation.compiler.shell.scp_file')
	@mock.patch('compilation.compiler.shell.execute_command')
	def test_build_singularity_container(self, mock_shell, mock_scp):
		"""
		It test the correct work of the function
		create_singularity_image
		"""

		filename = compiler.build_singularity_container('asdf@asdf.com', '/test/test.def', 'image.img', '/tmp')

		#mock_shell.assert_called_with('sudo', 'asdf@asdf.com', ['singularity', 'bootstrap', 'image.img', 'test.def'])
		mock_scp.assert_called_with(filename, 'asdf@asdf.com', 'image.img', False)

		filename = filename[5:-4]

		try:
			val = UUID(filename, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + filename)

		# In case not necessary to use sudo
		filename = compiler.build_singularity_container('asdf@asdf.com', '/test/test.def', 'image.img', '/tmp', become=False)

		#mock_shell.assert_called_with('singularity', 'asdf@asdf.com', ['bootstrap', 'image.img', 'test.def'])
		mock_scp.assert_called_with(filename, 'asdf@asdf.com', 'image.img', False)

		filename = filename[5:-4]

		try:
			val = UUID(filename, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + filename)

		# In case of local compilation
		filename = compiler.build_singularity_container('', '/test/test.def', 'image.img', '/tmp', become=False)

		filename = filename[5:-4]

		try:
			val = UUID(filename, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + filename)

		## WE VERIFY ALL THE CALLS:

		call_1 = call('sudo', 'asdf@asdf.com', ['singularity', 'bootstrap', 'image.img', 'test.def'])
		call_2 = call('singularity', 'asdf@asdf.com', ['bootstrap', 'image.img', 'test.def'])
		call_3 = call('singularity', '', ['bootstrap', 'image.img', 'test.def'])
		call_4 = call('mv', '', [ANY, ANY])
		calls = [ call_1, call_2, call_3, call_4]
		mock_shell.assert_has_calls(calls)


	@mock.patch('compilation.compiler.shell.execute_command')
	def test_create_singularity_image(self, mock_shell):
		"""
		It test the correct work of the funciton:
		create_singularity_template
		"""

		config.COMPILATION_CONFIG_FILE = "compilation_config.json"
		configuration = config.find_compilation_config('SINGULARITY:PM')

		compiler.create_singularity_image(configuration, 'asdf@asdf.com', 'singularity_pm.img')

		mock_shell.assert_called_with('singularity', 'asdf@asdf.com', [ 'create', '-F', '--size', '4096', 'singularity_pm.img'])



	@mock.patch('compilation.compiler.shell.scp_file')
	@mock.patch('compilation.template.update_template')
	def test_create_singularity_template(self, mock_template, mock_scp):
		"""
		It test the correct work of the function craete singularity template
		"""

		configuration = { 'singularity_template': 'sing_template'}
		executable = Executable('test.zip', 'comp_script', 'xxxx')

		mock_template.return_value = 'sing_template'

		template = compiler.create_singularity_template(configuration, executable, 'asdf@asdf.com', 'comp_folder')

		self.assertEquals('sing_template', template)

		mock_template.assert_called_with('sing_template', 'comp_script', 'comp_folder')
		mock_scp.assert_called_with('sing_template', 'asdf@asdf.com', '.')


	@mock.patch("compilation.compiler.shell.execute_command")
	def test_unzip_src(self, mock_shell_execute):
		"""
		It verifies the workflow of unziping the zip file
		"""

		executable = Executable('test.zip', 'xxxx', 'xxxx')

		compiler.unzip_src(executable, 'asd@asdf.com', '/home/pepito')

		zip_file = os.path.join('/home/pepito', 'test.zip')

		mock_shell_execute.assert_called_with('unzip', 'asd@asdf.com', [ zip_file, '-d', '/home/pepito'])

	@mock.patch("compilation.compiler.shell.execute_command")
	def test_create_random_folder(self, mock_shell_excute):
		""" Test the creation of a random folder in a server """

		destination_folder = compiler.create_random_folder('server@xxxx:2222')

		try:
			val = UUID(destination_folder, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + destination_folder)

		mock_shell_excute.assert_called_with("mkdir", "server@xxxx:2222", [ destination_folder ])

	@mock.patch('compilation.compiler.shell.execute_command')
	@mock.patch('compilation.compiler.shell.scp_file')
	def test_upload_zip_file_application(self, mock_scp, mock_exec):
		""" 
		Test the function of uploading a zip file of the application 
		to the selected testbed in an specific folder
		"""

		executable = Executable('test.zip', 'xxxx', 'xxxx')

		compiler.upload_zip_file_application(executable, 'asd@asdf.com', 'dest_folder', '/tmp')

		mock_scp.assert_called_with(os.path.join('/tmp', 'test.zip'), 'asd@asdf.com', './dest_folder')

		compiler.upload_zip_file_application(executable, '', 'dest_folder', '/tmp')

		mock_exec.assert_called_with('cp', params=[ os.path.join('/tmp', 'test.zip'), './dest_folder'])
