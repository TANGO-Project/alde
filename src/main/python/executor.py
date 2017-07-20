# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from threading import Thread
from models import db, Execution, Testbed

execute_type_slurm_sbatch = "slurm:sbatch"
execute_status_submitted = "SUBMITTED"
execute_status_failed = "FAILED"


def execute_application(execution_script):
	"""
	This function executes an application in the selected testbed,
	using the execution script configuration.
	"""

	# We create the execution
	execution = Execution(execution_script.command,
						  execution_script.execution_type,
						  execution_script.parameters,
						  execute_status_submitted)
	
	execution_script.executions.append(execution)

	db.session.commit()

	# We verify that we recoginze the type of execution
	if execution.execution_type == execute_type_slurm_sbatch :

		t = Thread(target=execute_application_type_slurm_sbatch, args=(execution,))
		t.start()
		return t
	else: 
		execution.status = execute_status_failed
		execution.output = "No support for execurtion type: " + execution.execution_type
		db.session.commit()

def execute_application_type_slurm_sbatch(execution):
	"""
	Executes an application with a device supervisor configured
	for slurm sbatch
	"""

	testbed = execution.execution_script.testbed

	if testbed.category is not Testbed.slurm_category:
		# If the category is not SLURM we can not execute the app
		execution.status = execute_status_failed
		execution.output = "Testbed does not support " + execute_type_slurm_sbatch + " applications"
		db.session.commit()

	elif not testbed.on_line :
		# If the testbed is off-line is not SLURM we can not execute the app
		execution.status = execute_status_failed
		execution.output = "Testbed is off-line"
		db.session.commit()