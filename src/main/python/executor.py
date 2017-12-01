# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from threading import Thread
from models import db, Execution, Testbed, Executable, Deployment, ExecutionConfiguration
import shell
import uuid
import os
import logging

execute_type_slurm_sbatch = "slurm:sbatch"
execute_type_singularity_pm = "SINGULARITY:PM"
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
	elif execution.execution_type == execute_type_singularity_pm :
		t = Thread(target=execute_application_type_singularity_pm, args=(execution, execution_configuration.id))
		t.start()
		return t
	else: 
		execution.status = execute_status_failed
		execution.output = "No support for execurtion type: " + execution.execution_type
		db.session.commit()

def execute_application_type_singularity_pm(execution, identifier):
	"""
	It executes a Singularity PM application in a targatted testbed
	"""

	# Lets recover all the information needed...execution_configuration
	execution_configuration = db.session.query(ExecutionConfiguration).filter_by(id=identifier).first() # This is to avoid reusing objects from other thread
	testbed = db.session.query(Testbed).filter_by(id=execution_configuration.testbed_id).first()
	deployment = db.session.query(Deployment).filter_by(executable_id=execution_configuration.executable_id, testbed_id=testbed.id).first()
	executable = db.session.query(Executable).filter_by(id=execution_configuration.executable_id).first()

	# Preparing the command to be executed
	command = "source"
	endpoint = testbed.endpoint
	params = []
	params.append(testbed.extra_config['enqueue_env_file'])
	params.append(";")
	params.append("enqueue_compss")
	params.append("--sc_cfg=" + testbed.extra_config['enqueue_compss_sc_cfg'])
	params.append("--num_nodes=" + str(execution_configuration.num_nodes))
	params.append("--gpus_per_node=" + str(execution_configuration.num_gpus_per_node))
	params.append("--cpus_per_node=" + str(execution_configuration.num_cpus_per_node))
	params.append("--container_image=" + deployment.path)
	params.append("--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/") # TODO Ugly... ugly... and more ugly...
	#params.append("--appdir=" + executable.singularity_app_folder)
	params.append("--appdir=/apps/application/") # TODO Ugly... fix this... 
	params.append("--exec_time=" + str(execution_configuration.exec_time))
	params.append(execution_configuration.compss_config)
	params.append(execution_configuration.command)

	logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

	output = shell.execute_command(command, endpoint, params)
	sbatch_id = __extract_id_from_sigularity_pm_app__(output)
	
	execution = Execution(execution_configuration.execution_type, Execution.__status_running__)
	execution_configuration.executions.append(execution)
	execution.slurm_sbatch_id = sbatch_id
	db.session.commit()

def execute_application_type_singularity_srun(execution, identifier):
	"""
	It supports execution of this type:
	( srun -N 2 -n 16 singularity run /home_nfs/home_dineshkr/UseCaseMiniAppBuild/ALDE/centos-7-clover-leaf-mpi.img > allout.txt 2>&1 & ) ; sleep 1; squeue
	"""

	# Lets recover all the information needed...execution_configuration
	execution_configuration = db.session.query(ExecutionConfiguration).filter_by(id=identifier).first() # This is to avoid reusing objects from other thread
	testbed = db.session.query(Testbed).filter_by(id=execution_configuration.testbed_id).first()
	deployment = db.session.query(Deployment).filter_by(executable_id=execution_configuration.executable_id, testbed_id=testbed.id).first()
	executable = db.session.query(Executable).filter_by(id=execution_configuration.executable_id).first()

	# Preparing the command to be executed
	command = "("
	endpoint = testbed.endpoint
	params = []
	params.append("srun")
	if execution_configuration.num_nodes:
		params.append("-N")
		params.append(str(execution_configuration.num_nodes))
	if execution_configuration.num_gpus_per_node:
		params.append("-gres=" + str(execution_configuration.num_gpus_per_node))
	params.append("-n")
	params.append(str(execution_configuration.num_cpus_per_node))
	params.append("singularity")
	params.append("run")
	params.append(deployment.path)
	params.append("&")
	params.append(")")
	params.append(";")
	params.append("sleep")
	params.append("1;")
	params.append("squeue")

	logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

	output = shell.execute_command(command, endpoint, params)
	sbatch_id = __extract_id_from_squeue__(output)
	
	execution = Execution(execution_configuration.execution_type, Execution.__status_running__)
	execution_configuration.executions.append(execution)
	execution.slurm_sbatch_id = sbatch_id
	db.session.commit()

def __extract_id_from_squeue__(output):
	"""
	It extracts the id from squeue output
	"""

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	last = None
	for line in (line for line in lines if line.rstrip('\n')):
		last = line

	last = ' '.join(last.split())
	return int(last.split()[0])

def __extract_id_from_sigularity_pm_app__(output):
	"""
	Internal method to extract the id from the output of
	the execution of enqueue_compss commnad
	"""

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	last = None
	for line in (line for line in lines if line.rstrip('\n')):
		last = line

	last = ' '.join(last.split())
	return int(last.split()[-1])

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

			shell.execute_command('mkdir', testbed.endpoint, [ path ])

			filename = os.path.basename(executable.singularity_image_file)

			path = path + "/"
			deployment.path = os.path.join(path, filename)

			# Uploading the file to the testbed
			shell.scp_file(executable.singularity_image_file, testbed.endpoint, path)

			deployment.status = Deployment.__status_uploaded_updated__
			db.session.commit()

def monitor_execution_apps():
	"""
	It monitors which apps have running executions.
	It check the status fo those running apps and updates the db accordingly
	"""

	# TODO query que encuentre las apps que están corriendo y las devuelva 
	executions = db.session.query(Execution).filter_by(status=Execution.__status_running__).all()

	for execution in executions :

		if execution.execution_type == Executable.__type_singularity_pm__ :
			status = monitor_execution_singularity_apps(execution)
			execution.status = status
			db.session.commit()



def monitor_execution_singularity_apps(execution):
	"""	
	It monitors the execution of singularity applications
	"""

	sbatch_id = execution.slurm_sbatch_id
	testbed = execution.execution_configuration.testbed

	status = _parse_sacct_output(sbatch_id, testbed.endpoint)

	if status == '?':
		return execution.status
	else:
		return status

def _parse_sacct_output(id, url):
	"""
	It executes the sacct command and extracts the status
	information
	"""

	output = shell.execute_command('sacct', server=url, params=['-j', id, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
	
	if output.count(b'\n') <= 2:
		return '?'
	elif output.count(b'RUNNING') >= 1:
		return 'RUNNING'
	elif output.count(b'FAILED') >= 1:
		return 'FAILED'
	elif output.count(b'COMPLETED') >= 1:
		return 'COMPLETED'
	else:
		return 'UNKNOWN'
	
def find_squeue_job_status(command_output):
	"""
	It finds the status of a squeue job:

	PENDING (PD), RUNNING (R), SUSPENDED (S), STOPPED (ST), COMPLETING (CG), COMPLETED (CD), CONFIGURING (CF), CANCELLED (CA), FAILED (F), TIMEOUT (TO), PREEMPTED (PR), BOOT_FAIL (BF) , NODE_FAIL (NF), REVOKED (RV), and SPECIAL_EXIT (SE)

	it returns "UNKNOWN" if it was not in the command output
	"""

	output = shell.execute_command('squeue', testbed.endpoint, [])

	lines = output.decode('utf-8')
	lines = lines.split("\n")


	pass
