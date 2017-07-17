# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import executor
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Execution, ExecutionScript

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	def test_execute_application(self):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_script = ExecutionScript("ls", "slurm:sbatch", "-x1")
		db.session.add(execution_script)
		db.session.commit()

		executor.execute_application(execution_script)

		execution_script = db.session.query(ExecutionScript).filter_by(command="ls").first()

		self.assertEquals(1, len(execution_script.executions))
		execution = execution_script.executions[0]
		self.assertEquals("ls", execution.command)
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals("-x1", execution.parameters)
		self.assertEquals(executor.execute_status_submitted, execution.status)