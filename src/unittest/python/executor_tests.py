# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import executor
import unittest.mock as mock
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Execution, ExecutionConfiguration, Testbed

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	@mock.patch("executor.execute_application_type_slurm_sbatch")
	def test_execute_application(self, mock_slurm_sbatch):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_configuration = ExecutionConfiguration("ls", "slurm:sbatch", "-x1")
		db.session.add(execution_configuration)
		db.session.commit()

		t = executor.execute_application(execution_configuration)

		execution = db.session.query(Execution).filter_by(command="ls").first()
		self.assertEquals("ls", execution.command)
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals("-x1", execution.parameters)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_sbatch.assert_called_with(execution)

		# We verify the wrong status of unrecognize execution type
		execution_configuration.execution_type = "xxx"
		db.session.commit()

		executor.execute_application(execution_configuration)

		execution = db.session.query(Execution).filter_by(execution_type="xxx").first()
		self.assertEquals("ls", execution.command)
		self.assertEquals("xxx", execution.execution_type)
		self.assertEquals("-x1", execution.parameters)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("No support for execurtion type: xxx", execution.output)

	def test_execute_application_type_slurm_sbatch(self):
		"""
		It verifies that the application type slurm sbatch is executed
		"""

		# First we verify that the testbed is of type SLURM to be able
		# to execute it, in this case it should give an error since it is
		# not of type slurm

		execution = Execution("ls", "slurm:sbatch", "-X", executor.execute_status_submitted)
		testbed = Testbed("name", True, "xxxx", "ssh", "user@server", ['slurm'])
		execution_configuration = ExecutionConfiguration("ls", "slurm:sbatch", "-x1")
		execution.execution_configuration=execution_configuration
		execution_configuration.testbed = testbed

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("ls", execution.command)
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals("-X", execution.parameters)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed does not support slurm:sbatch applications", execution.output)

		# If the testbed is off-line, execution isn't allowed also
		testbed.category = Testbed.slurm_category
		testbed.on_line = False
		execution.status = executor.execute_status_submitted

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("ls", execution.command)
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals("-X", execution.parameters)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed is off-line", execution.output)

