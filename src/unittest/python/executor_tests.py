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
from models import db, Execution, ExecutionScript

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	@mock.patch("executor.execute_application_type_slurm_sbatch")
	def test_execute_application(self, mock_slurm_sbatch):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_script = ExecutionScript("ls", "slurm:sbatch", "-x1")
		db.session.add(execution_script)
		db.session.commit()

		t = executor.execute_application(execution_script)

		execution_script = db.session.query(ExecutionScript).filter_by(command="ls").first()

		self.assertEquals(1, len(execution_script.executions))
		execution = execution_script.executions[0]
		self.assertEquals("ls", execution.command)
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals("-x1", execution.parameters)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_sbatch.assert_called_with(execution)

		# We verify the wrong status of unrecognize execution type
		execution_script.execution_type = "xxx"
		db.session.commit()

		executor.execute_application(execution_script)

		execution_script = db.session.query(ExecutionScript).filter_by(command="ls").first()

		self.assertEquals(2, len(execution_script.executions))
		execution = execution_script.executions[1]
		self.assertEquals("ls", execution.command)
		self.assertEquals("xxx", execution.execution_type)
		self.assertEquals("-x1", execution.parameters)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("No support for execurtion type: xxx", execution.output)