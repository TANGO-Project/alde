# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import executor
import os
import shell
import unittest.mock as mock
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Execution, Deployment, ExecutionConfiguration, Testbed, Executable
from uuid import UUID

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	@mock.patch("shell.execute_command")
	@mock.patch("shell.scp_file")
	def test_upload_deployment(self, mock_scp, mock_execute):
		""" Verifies that the upload of the deployment works """

		executable = Executable("source", "script", "TYPE")
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable("source", "script", "SINGULARITY:PM")
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SBATCH" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable("source", "script", "SINGULARITY:PM")
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )
		executable.status = Executable.__status_compiled__
		executable.singularity_image_file='file.img'
		db.session.add(executable)
		db.session.add(testbed)
		db.session.commit()

		deployment = Deployment()
		deployment.executable_id = executable.id
		deployment.testbed_id = testbed.id

		db.session.add(deployment)
		db.session.commit()

		executor.upload_deployment(executable, testbed)
		deployment = db.session.query(Deployment).filter_by(executable_id=executable.id, testbed_id=testbed.id).first()
		path = deployment.path[:36] # Extracting the UUID
		try:
			val = UUID(path, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + path)

		self.assertEquals(Deployment.__status_uploaded_updated__, deployment.status)

		# We verify the calls to shell
		mock_execute.assert_called_with('mkdir', testbed.endpoint, [ path ])
		local_filename = os.path.join('/tmp', executable.singularity_image_file)
		mock_scp.assert_called_with(local_filename, testbed.endpoint, path)

	@mock.patch("executor.execute_application_type_slurm_sbatch")
	def test_execute_application(self, mock_slurm_sbatch):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_configuration = ExecutionConfiguration()
		execution_configuration.execution_type = "slurm:sbatch"
		db.session.add(execution_configuration)
		db.session.commit()

		t = executor.execute_application(execution_configuration)

		execution = db.session.query(Execution).filter_by(execution_type="slurm:sbatch").first()
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_sbatch.assert_called_with(execution)

		# We verify the wrong status of unrecognize execution type
		execution_configuration.execution_type = "xxx"
		db.session.commit()

		executor.execute_application(execution_configuration)

		execution = db.session.query(Execution).filter_by(execution_type="xxx").first()
		self.assertEquals("xxx", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("No support for execurtion type: xxx", execution.output)

	def test_execute_application_type_slurm_sbatch(self):
		"""
		It verifies that the application type slurm sbatch is executed
		"""

		# First we verify that the testbed is of type SLURM to be able
		# to execute it, in this case it should give an error since it is
		# not of type slurm

		execution = Execution("slurm:sbatch", executor.execute_status_submitted)
		testbed = Testbed("name", True, "xxxx", "ssh", "user@server", ['slurm'])
		execution_configuration = ExecutionConfiguration()
		execution_configuration.execution_type = "slurm:sbatch"
		execution.execution_configuration=execution_configuration
		execution_configuration.testbed = testbed

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed does not support slurm:sbatch applications", execution.output)

		# If the testbed is off-line, execution isn't allowed also
		testbed.category = Testbed.slurm_category
		testbed.on_line = False
		execution.status = executor.execute_status_submitted

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed is off-line", execution.output)

