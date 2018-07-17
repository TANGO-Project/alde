# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from models import Execution

class ExecutionTests(unittest.TestCase):
	"""
	Unit test for the class Execution inside the models package
	"""

	def test_initialization_execution(self):
		"""Test the initializacion method of the class Execution"""

		execution = Execution()
		execution.execution_type = "execution_type"
		execution.status = "status"

		self.assertEquals("execution_type", execution.execution_type)
		self.assertEquals("status", execution.status)
	
	def test_get_number_extra_jobs(self):
		"""
		Tests the correct work of the method  get_number_extra_jobs
		"""

		execution = Execution()
		execution.execution_type = "execution_type"
		execution.status = "status"
		self.assertEquals(0, execution.get_number_extra_jobs())

		execution.extra_slurm_job_id = ''
		self.assertEquals(0, execution.get_number_extra_jobs())

		execution.extra_slurm_job_id = '     '
		self.assertEquals(0, execution.get_number_extra_jobs())

		execution.extra_slurm_job_id = ' 12    232   4443  5663     23234        '
		self.assertEquals(5, execution.get_number_extra_jobs())