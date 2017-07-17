# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from models import db, Execution

execute_status_submitted = "SUBMITTED"

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