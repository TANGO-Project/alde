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
from sqlalchemy import or_
from flask import current_app as app

execute_type_slurm_sbatch = Executable.__type_slurm_sbatch__
execute_type_singularity_pm = Executable.__type_singularity_pm__
execute_type_singularity_srun = Executable.__type_singularity_srun__
execute_type_slurm_srun = Executable.__type_slurm_srun__
execute_status_submitted = "SUBMITTED"
execute_status_failed = "FAILED"


def execute_application(execution_configuration, create_profile=False, use_stored_profile=False):
	"""
	This function executes an application in the selected testbed,
	using the execution script configuration.
	"""

	# We create the execution
	execution = Execution()
	execution.execution_type = execution_configuration.execution_type
	execution.status = execute_status_submitted

	profile_folder = app.config['APP_PROFILE_FOLDER']
	
	db.session.add(execution)

	db.session.commit()

	# We verify that we recoginze the type of execution
	if execution.execution_type == execute_type_slurm_sbatch :

		t = Thread(target=execute_application_type_slurm_sbatch, args=(execution, execution_configuration.id))
		t.start()
		return t
	elif execution.execution_type == execute_type_singularity_pm :
		t = Thread(target=execute_application_type_singularity_pm, 
		           args=(execution, execution_configuration.id, create_profile, use_stored_profile, profile_folder))
		t.start()
		return t
	elif execution.execution_type == execute_type_singularity_srun :
		t = Thread(target=execute_application_type_singularity_srun, args=(execution, execution_configuration.id))
		t.start()
		return t
	elif execution.execution_type == execute_type_slurm_srun :
		t = Thread(target=execute_application_type_slurm_srun, args=(execution, execution_configuration.id))
		t.start()
		return t
	else: 
		execution.status = execute_status_failed
		execution.output = "No support for execurtion type: " + execution.execution_type
		db.session.commit()

def execute_application_type_singularity_pm(execution, identifier, create_profile=False, use_storage_profile=False, profile_folder='.'):
	"""
	It executes a Singularity PM application in a targatted testbed
	"""

	# If create_profile = True we need to create a profile and associate it with the execution
	profile_file = ''
	if create_profile :
		profile_file = profile_folder + '/' + str(uuid.uuid4()) + '.profile'

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
	# If create profile
	if create_profile :
		params.append("--output_profile=" + profile_file)
	# If we use a profile  --output_profile=<path>
	if use_storage_profile :
		params.append("--input_profile=" + execution_configuration.profile_file)
	params.append(execution_configuration.compss_config)
	params.append(execution_configuration.command)

	logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

	output = shell.execute_command(command, endpoint, params)
	sbatch_id = __extract_id_from_sigularity_pm_app__(output)
	
	execution = Execution()
	execution.execution_type = execution_configuration.execution_type
	execution.status = Execution.__status_running__
	execution_configuration.executions.append(execution)
	# if we create the profile, we add it to the execution configuration
	if create_profile :
		execution_configuration.profile_file = profile_file
	execution.slurm_sbatch_id = sbatch_id
	db.session.commit()

def __get_srun_info__(execution, identifier):
	"""
	Internal method that gets all the necessary srun information
	"""

	# Lets recover all the information needed...execution_configuration
	execution_configuration = db.session.query(ExecutionConfiguration).filter_by(id=identifier).first() # This is to avoid reusing objects from other thread
	testbed = db.session.query(Testbed).filter_by(id=execution_configuration.testbed_id).first()
	deployment = db.session.query(Deployment).filter_by(executable_id=execution_configuration.executable_id, testbed_id=testbed.id).first()
	executable = db.session.query(Executable).filter_by(id=execution_configuration.executable_id).first()

	return execution_configuration, testbed, deployment, executable


def execute_application_type_slurm_srun(execution, identifier):
	"""
	It supports execution of this type:
	( srun --job-name gromacstest 
	       --profile=energy,task 
	       --acctg-freq=Energy=1,Task=1 
	       --gres=gpu 
	       -n 1 
	       /usr/local/gromacs-4.6.7-cuda2/bin/mdrun -s /home_nfs/home_dineshkr/Gromacs/gromacs-run/peptide_water_3k.tpr -v -nsteps 50000 -testverlet > allout.txt 2>&1 & ) ; sleep 1 ; squeue
	"""

	execution_configuration, testbed, deployment, executable = __get_srun_info__(execution, identifier)

	# Preparing the command to be executed
	command = "("
	endpoint = testbed.endpoint
	params = []
	params.append("srun")
	if execution_configuration.num_nodes:
		params.append("-N")
		params.append(str(execution_configuration.num_nodes))
	if execution_configuration.num_gpus_per_node:
		params.append("--gres=gpu:" + str(execution_configuration.num_gpus_per_node))
	params.append("-n")
	params.append(str(execution_configuration.num_cpus_per_node))
	if execution_configuration.srun_config:
		params.append(execution_configuration.srun_config)
	params.append(executable.executable_file)
	params.append(execution_configuration.command)
	params.append(">")
	params.append("allout.txt")
	params.append("2>&1")
	params.append("&")
	params.append(")")
	params.append(";")
	params.append("sleep")
	params.append("1;")
	params.append("squeue")

	logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

	__launch_execution__(command, endpoint, params, execution_configuration)


def execute_application_type_singularity_srun(execution, identifier):
	"""
	It supports execution of this type:
	( srun -N 2 -n 16 singularity run /home_nfs/home_dineshkr/UseCaseMiniAppBuild/ALDE/centos-7-clover-leaf-mpi.img > allout.txt 2>&1 & ) ; sleep 1; squeue
	"""

	execution_configuration, testbed, deployment, executable = __get_srun_info__(execution, identifier)

	# Preparing the command to be executed
	command = "("
	endpoint = testbed.endpoint
	params = []
	params.append("srun")
	if execution_configuration.num_nodes:
		params.append("-N")
		params.append(str(execution_configuration.num_nodes))
	if execution_configuration.num_gpus_per_node:
		params.append("--gres=gpu:" + str(execution_configuration.num_gpus_per_node))
	params.append("-n")
	params.append(str(execution_configuration.num_cpus_per_node))
	params.append("singularity")
	params.append("run")
	params.append(deployment.path)
	params.append(">")
	params.append("allout.txt")
	params.append("2>&1")
	params.append("&")
	params.append(")")
	params.append(";")
	params.append("sleep")
	params.append("1;")
	params.append("squeue")

	logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

	__launch_execution__(command, endpoint, params, execution_configuration)

def __launch_execution__(command, endpoint, params, execution_configuration):
	"""
	It updates after any srun execution, singularity or not
	"""

	output = shell.execute_command(command, endpoint, params)
	sbatch_id = __extract_id_from_squeue__(output)
	
	execution = Execution()
	execution.execution_type = execution_configuration.execution_type
	execution.status = Execution.__status_running__
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

def execute_application_type_slurm_sbatch(execution, identifier):
	"""
	Executes an application with a device supervisor configured
	for slurm sbatch
	"""

	execution_configuration, testbed, deployment, executable = __get_srun_info__(execution, identifier)

	if testbed.category != Testbed.slurm_category:
		# If the category is not SLURM we can not execute the app
		execution.status = execute_status_failed
		execution.output = "Testbed does not support " + execute_type_slurm_sbatch + " applications"
		db.session.commit()

	elif not testbed.on_line :
		# If the testbed is off-line is not SLURM we can not execute the app
		execution.status = execute_status_failed
		execution.output = "Testbed is off-line"
		db.session.commit()

	else:
		# Preparing the command to be executed
		command = "sbatch"
		endpoint = testbed.endpoint
		params = []
		params.append(executable.executable_file)

		logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))

		output = shell.execute_command(command, endpoint, params)
		print(output)

		sbatch_id = __extract_id_from_sbatch__(output)
		
		execution = Execution()
		execution.execution_type = execution_configuration.execution_type
		execution.status = Execution.__status_running__
		execution_configuration.executions.append(execution)
		execution.slurm_sbatch_id = sbatch_id
		db.session.commit()

def __extract_id_from_sbatch__(output):
	"""
	It parses the sbatch command output
	"""

	output = output.decode('utf-8')
	output = output.split()
	return output[-1]


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

	executions = db.session.query(Execution).filter(or_(Execution.status == Execution.__status_running__, Execution.status == Execution.__status_cancel__)).all()

	for execution in executions :

		if execution.execution_type == Executable.__type_singularity_pm__ or execution.execution_type == Executable.__type_singularity_srun__ or execution.execution_type == Executable.__type_slurm_srun__ or execution.execution_type == Executable.__type_slurm_sbatch__:
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

def cancel_execution(execution, url):
	"""
	It finds an execution an cancels it if running
	"""

	if (( execution.execution_type == execute_type_singularity_pm ) or ( execution.execution_type == execute_type_singularity_srun ) or ( execution.execution_type == execute_type_singularity_srun ) or ( execution.execution_type == execute_type_slurm_srun )) and ( execution.status == Execution.__status_running__ ) :
		
		if execution.extra_slurm_job_id is not None and execution.extra_slurm_job_id != '' :
			for id_to_remove in execution.extra_slurm_job_id.split():
				shell.execute_command('scancel', url, [ id_to_remove ])

		shell.execute_command('scancel', url, [ str(execution.slurm_sbatch_id) ])

def remove_resource(execution):
	"""
	it removes resources to a running execution:
		adapt_compss_resources <master_node> <master_job_id> REMOVE SLURM-Cluster <node_to_delete>
		adapt_compss_resources ns51 7262 REMOVE SLURM-Cluster ns50
	"""

	if (( execution.execution_type == execute_type_singularity_pm)) :
		logging.info("Executing type corresponds with SINGULARITY_PM, trying adaptation")

		if (( execution.status == Execution.__status_running__)) :
			url = execution.execution_configuration.testbed.endpoint
			enqueue_env_file = execution.execution_configuration.testbed.extra_config['enqueue_env_file']
			sbatch_id = execution.slurm_sbatch_id
			id_returned, ids = id_to_remove(execution.extra_slurm_job_id)
			
			if id_returned is not None :
				node = find_first_node(sbatch_id, url)
				node_job_to_remove = find_first_node(id_returned, url)

				command = "source"
				params = []
				params.append(enqueue_env_file)
				params.append(";")
				params.append("adapt_compss_resources")
				params.append(node)
				params.append(sbatch_id)
				params.append('REMOVE SLURM-Cluster')
				params.append(node_job_to_remove)
				output = shell.execute_command(command, url, params)

				if verify_adaptation_went_ok(output) :
					logging.info("Adaptation performed ok")
					execution.extra_slurm_job_id = ids
					db.session.commit()
				else:
					logging.info("There was an error in the adaptation:")
					output = output.decode('utf-8')
					logging.info(output)
					
			else :
				logging.info("No extra jobs to be able to delete")
		else :
			logging.info("Execution is not in RUNNING status, no action can be done")
	else :
		logging.info("Execution: " + execution.execution_type + " it is not compatible with add resource action")

def add_resource(execution):
	"""
	it adds resources to a running execution

	    adapt_compss_resources <master_node> <master_job_id> CREATE SLURM-Cluster default <singularity_image> 
	"""

	if (( execution.execution_type == execute_type_singularity_pm)) :
		logging.info("Executing type corresponds with SINGULARITY_PM, trying adaptation")

		if (( execution.status == Execution.__status_running__)) :
			url = execution.execution_configuration.testbed.endpoint
			scaling_upper_bound = execution.execution_configuration.application.scaling_upper_bound
			enqueue_env_file = execution.execution_configuration.testbed.extra_config['enqueue_env_file']
			singularity_image_file = execution.execution_configuration.executable.singularity_image_file
			sbatch_id = execution.slurm_sbatch_id


			upper_bound_ok = True
			if ( scaling_upper_bound is not None ) and ( scaling_upper_bound != 0 ) :
				if scaling_upper_bound <= execution.get_number_extra_jobs() :
					upper_bound_ok = False

			if upper_bound_ok :
				node = find_first_node(sbatch_id, url)

				command = "source"
				params = []
				params.append(enqueue_env_file)
				params.append(";")
				params.append("adapt_compss_resources")
				params.append(node)
				params.append(sbatch_id)
				params.append('CREATE SLURM-Cluster default')
				params.append(singularity_image_file)
				output = shell.execute_command(command, url, params)

				job_name = parse_add_resource_output(output)
				extra_job_id = get_job_id_after_adaptation(job_name, url) 

				if extra_job_id != '' or extra_job_id is not None :
					if execution.extra_slurm_job_id is None :
						execution.extra_slurm_job_id = extra_job_id
					else :
						execution.extra_slurm_job_id = execution.extra_slurm_job_id + ' ' + extra_job_id
					db.session.commit()
			else :
				logging.info('Execution already reached its maximum number of extra jobs, no adaptation possible')
		else :
			logging.info("Execution is not in RUNNING status, no action can be done")
	else :
		logging.info("Execution: " + execution.execution_type + " it is not compatible with add resource action")

def find_first_node(sbatch_id, url):
	"""
	This method finds the first node of a job using squeue command
	garciad@ns54 ~]$ squeue -j 7035 -o %N
	NODELIST
	ns51
	"""

	output = shell.execute_command("squeue", url , [ '-j', sbatch_id, '-o', '%N' ])

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	last = None
	for line in (line for line in lines if line.rstrip('\n')):
		last = line

	last = last.strip()
	nodes = last.split(',')
	nodes = nodes[0]

	if '[' in nodes :
		parts = nodes.split('[')
		node_name = parts[0]
		node_numbers = parts[1]
		first_number = node_numbers.split('-')[0]
		return node_name + first_number
	else :
		return nodes

def parse_add_resource_output(output):
	"""
	It parses the add resource output of COMPs to 
	get the job name
	"""

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	searched_line = ''
	for line in (line for line in lines if line.rstrip('\n')):
		if '[Adaptation] Read ACK' in line:
			searched_line = line

	items = searched_line.split()

	if len(items) > 0:
		return searched_line.split()[-1]
	else :
		 return ''

def get_job_id_after_adaptation(job_name, url):
	"""
	It executes the following squeue line to get the job ID
	squeue --name=job_name -h -o %A
	"""

	output = shell.execute_command("squeue", url , [ '--name=' + job_name, '-h', '-o', '%A' ])

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	return lines[0].strip()

def id_to_remove(ids):
	"""
	It takes a collection of string ids, if possible, it returns the last one

	Returns none if ids are empty
	"""

	if ids is None :
		return None, None
	elif ids == '' :
		return None, ''
	else :
		list_of_ids = ids.split()
		last = list_of_ids.pop()
		ids = ' '.join(list_of_ids)
		return last, ids

def verify_adaptation_went_ok(output):
	"""
	It verifies the message has got an ACK

	Cluster default /home_nfs/home_ejarquej/matmul-cuda8-y3.img
    COMPSS_HOME=/home_nfs/home_ejarquej/installations/2.2.6/COMPSs
    [Adaptation] writting command CREATE SLURM-Cluster default /home_nfs/home_ejarquej/matmul-cuda8-y3.img on /fslustre/tango/matmul/log_dir/.COMPSs/7065/adaptation/command_pipe
    [Adaptation] Reading result /fslustre/tango/matmul/log_dir/.COMPSs/7065/adaptation/result_pipe
    [Adaptation] Read ACK
    [Adaptation]

	it returns true if the message has [Adaptation] Read ACK, false otherwise
	"""

	lines = output.decode('utf-8')
	lines = lines.split("\n")

	ok = False
	for line in (line for line in lines if line.rstrip('\n')):
		if '[Adaptation] Read ACK' in line:
			ok = True

	return ok