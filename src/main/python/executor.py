# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from threading import Thread
from models import db, Execution, Testbed, Executable, Deployment
import shell
import uuid
import os

execute_type_slurm_sbatch = "slurm:sbatch"
execute_status_submitted = "SUBMITTED"
execute_status_failed = "FAILED"


def execute_application(execution_configuration):
	"""
	This function executes an application in the selected testbed,
	using the execution script configuration.
	"""

	# We create the execution
	execution = Execution(execution_configuration.execution_type,
						  execute_status_submitted)
	
	db.session.add(execution)

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

	testbed = execution.execution_configuration.testbed

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


def upload_deployment(executable, testbed, app_folder='/tmp'):
	"""
	It uploads a executable to the testbed to be executed
	"""
	# TODO app_folder needs to go via configuration.

	# TODO upload the executable
	# TODO Updates the status of the deployment

	if executable.compilation_type == Executable.__type_singularity_pm__ and testbed.category == Testbed.slurm_category and 'SINGULARITY' in testbed.package_formats :

		path = str(uuid.uuid4())

		if testbed.protocol == Testbed.protocol_ssh :
			# TODO for local protocol
			deployment = db.session.query(Deployment).filter_by(executable_id=executable.id, testbed_id=testbed.id).first()

			deployment.path = os.path.join(path, executable.singularity_image_file)
			

			shell.execute_command('mkdir', testbed.endpoint, [ path ])

			# Uploading the file to the testbed
			local_filename = os.path.join(app_folder, executable.singularity_image_file)
			shell.scp_file(local_filename, testbed.endpoint, path)

			deployment.status = Deployment.__status_uploaded_updated__
			db.session.commit()