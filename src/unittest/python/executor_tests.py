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
from models import db, Execution, Deployment, ExecutionConfiguration, Testbed, Executable, ExecutionConfiguration, Application
from uuid import UUID
from unittest.mock import call
from testfixtures import LogCapture

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	@mock.patch("shell.execute_command")
	@mock.patch("shell.scp_file")
	def test_upload_deployment(self, mock_scp, mock_execute):
		""" Verifies that the upload of the deployment works """

		executable = Executable()
		executable.source_code_file = 'source'
		executable.compilation_script = 'script'
		executable.compilation_type = 'TYPE'
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable()
		executable.source_code_file = 'source'
		executable.compilation_script = 'script'
		executable.compilation_type = "SINGULARITY:PM"
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SBATCH" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable()
		executable.source_code_file = 'source'
		executable.compilation_script = 'script'
		executable.compilation_type = "SINGULARITY:PM"
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )
		executable.status = Executable.__status_compiled__
		executable.singularity_image_file='/tmp/file.img'
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
		mock_scp.assert_called_with(executable.singularity_image_file, testbed.endpoint, path + "/")

	@mock.patch("executor.execute_application_type_slurm_srun")
	@mock.patch("executor.execute_application_type_singularity_srun")
	@mock.patch("executor.execute_application_type_singularity_pm")
	@mock.patch("executor.execute_application_type_slurm_sbatch")
	def test_execute_application(self, mock_slurm_sbatch, mock_singularity, mock_singularity_srun, mock_slurm_srun):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_configuration = ExecutionConfiguration()
		execution_configuration.execution_type = "SLURM:SBATCH"
		db.session.add(execution_configuration)
		db.session.commit()

		t = executor.execute_application(execution_configuration, False)

		execution = db.session.query(Execution).filter_by(execution_type="SLURM:SBATCH").first()
		self.assertEquals("SLURM:SBATCH", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_sbatch.assert_called_with(execution,  execution_configuration.id)

		execution_configuration.execution_type = "SINGULARITY:PM"
		db.session.commit()

		t = executor.execute_application(execution_configuration, False)
		execution = db.session.query(Execution).filter_by(execution_type="SINGULARITY:PM").first()
		self.assertEquals("SINGULARITY:PM", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_singularity.assert_called_with(execution, execution_configuration.id, False, False, '/profile_folder')

		# SINGULARITY:SRUN
		execution_configuration.execution_type = "SINGULARITY:SRUN"
		db.session.commit()

		t = executor.execute_application(execution_configuration, False)
		execution = db.session.query(Execution).filter_by(execution_type="SINGULARITY:SRUN").first()
		self.assertEquals("SINGULARITY:SRUN", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_singularity_srun.assert_called_with(execution, execution_configuration.id)

		# SLURM:SRUN
		execution_configuration.execution_type = "SLURM:SRUN"
		db.session.commit()

		t = executor.execute_application(execution_configuration, False)
		execution = db.session.query(Execution).filter_by(execution_type="SLURM:SRUN").first()
		self.assertEquals("SLURM:SRUN", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_srun.assert_called_with(execution, execution_configuration.id)

		# We verify the wrong status of unrecognize execution type
		execution_configuration.execution_type = "xxx"
		db.session.commit()

		executor.execute_application(execution_configuration, False)

		execution = db.session.query(Execution).filter_by(execution_type="xxx").first()
		self.assertEquals("xxx", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("No support for execurtion type: xxx", execution.output)

	@mock.patch("shell.execute_command")
	def test_execute_application_type_singularity_pm(self, mock_shell):
		"""
		It verifies the correct work of the function:
		execute_application_type_singularity_pm
		"""

		# We define the different entities necessaryb for the test.
		testbed = Testbed(name="nova2",
						  on_line=True,
						  category="SLURM",
						  protocol="SSH",
						  endpoint="user@testbed.com",
						  package_formats= ['sbatch', 'SINGULARITY'],
						  extra_config= {
						  	"enqueue_compss_sc_cfg": "nova.cfg" ,
						  	"enqueue_env_file": "/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv"
						  })
		db.session.add(testbed)

		application = Application(name="super_app")
		db.session.add(application)
		db.session.commit() # So application and testbed get an id

		executable = Executable()
		executable.source_code_file = 'test.zip'
		executable.compilation_script = 'gcc -X'
		executable.compilation_type = "SINGULARITY:PM"
		executable.singularity_app_folder="/singularity/app/folder"
		executable.singularity_image_file="pepito.img"
		executable.status = "COMPILED"
		executable.application = application
		db.session.add(executable)
		db.session.commit() # We do this so executable gets and id

		deployment = Deployment()
		deployment.testbed_id = testbed.id
		deployment.executable_id = executable.id
		deployment.path="/pepito/pepito.img"
		db.session.add(deployment) # We add the executable to the db so it has an id

		execution_config = ExecutionConfiguration()
		execution_config.execution_type ="SINGULARITY:PM"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		execution_config.num_nodes = 1
		execution_config.num_gpus_per_node = 2
		execution_config.num_cpus_per_node = 12
		execution_config.exec_time = 10 
		execution_config.command = "/apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_ejarquej/demo_test/cpu_gpu_run_data"
		execution_config.compss_config = "--worker_in_master_cpus=12 --worker_in_master_memory=24000 --worker_working_dir=/home_nfs/home_ejarquej --lang=c --monitoring=1000 -d"
		db.session.add(execution_config)
		db.session.commit()

		output = b'COMPSS_HOME=/home_nfs/home_ejarquej/installations/rc1707/COMPSs\nSC Configuration:          nova.cfg\nQueue:                     default\nReservation:               disabled\nNum Nodes:                 1\nNum Switches:              0\nGPUs per node:             2\nJob dependency:            None\nExec-Time:                 00:10:00\nStorage Home:              null\nStorage Properties:        \nOther:                     --sc_cfg=nova.cfg\n\t\t\t--gpus_per_node=2\n\t\t\t--cpus_per_node=12\n\t\t\t--container_image=/tmp/d96d4766-6612-414d-bf5e-0c043a3f30c3.img\n\t\t\t--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/\n\t\t\t--appdir=/apps/application/\n\t\t\t--worker_in_master_cpus=12\n\t\t\t--worker_in_master_memory=24000\n\t\t\t--worker_working_dir=/home_nfs/home_garciad\n\t\t\t--lang=c\n\t\t\t--monitoring=1000 -d /apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_garciad/demo_test/cpu_gpu_run_data\n \nTemp submit script is: /tmp/tmp.y7WxtgjPSz\nRequesting 2 processes\nSubmitted batch job 3357\n'

		mock_shell.return_value = output

		# TEST starts here:
		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_singularity_pm(execution, execution_config.id)

		mock_shell.assert_called_with("source",
									  "user@testbed.com",
									  [
									  	"/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv",
										";",
										"enqueue_compss",
										"--sc_cfg=nova.cfg",
										"--num_nodes=1",
										"--gpus_per_node=2",
										"--cpus_per_node=12",
										"--container_image=/pepito/pepito.img",
										"--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/",
										"--appdir=/apps/application/",
										"--exec_time=10",
										"--worker_in_master_cpus=12 --worker_in_master_memory=24000 --worker_working_dir=/home_nfs/home_ejarquej --lang=c --monitoring=1000 -d",
										"/apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_ejarquej/demo_test/cpu_gpu_run_data"
									   ]
									  )

		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()

		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(3357, execution.slurm_sbatch_id)

		# TEST with profile
		# TEST starts here:
		execution_config.profile_file = "/tmp/surperprofile.profile"
		db.session.commit()

		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_singularity_pm(execution, execution_config.id, use_storage_profile=True)

		mock_shell.assert_called_with("source",
									  "user@testbed.com",
									  [
									  	"/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv",
										";",
										"enqueue_compss",
										"--sc_cfg=nova.cfg",
										"--num_nodes=1",
										"--gpus_per_node=2",
										"--cpus_per_node=12",
										"--container_image=/pepito/pepito.img",
										"--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/",
										"--appdir=/apps/application/",
										"--exec_time=10",
										"--input_profile=/tmp/surperprofile.profile",
										"--worker_in_master_cpus=12 --worker_in_master_memory=24000 --worker_working_dir=/home_nfs/home_ejarquej --lang=c --monitoring=1000 -d",
										"/apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_ejarquej/demo_test/cpu_gpu_run_data"
									   ]
									  )

	def test__extract_id_from_sigularity_pm_app__(self):
		"""
		Test the correct work of the method: __extract_id_from_sigularity_pm_app__
		"""

		output = b'COMPSS_HOME=/home_nfs/home_ejarquej/installations/rc1707/COMPSs\nSC Configuration:          nova.cfg\nQueue:                     default\nReservation:               disabled\nNum Nodes:                 1\nNum Switches:              0\nGPUs per node:             2\nJob dependency:            None\nExec-Time:                 00:10:00\nStorage Home:              null\nStorage Properties:        \nOther:                     --sc_cfg=nova.cfg\n\t\t\t--gpus_per_node=2\n\t\t\t--cpus_per_node=12\n\t\t\t--container_image=/tmp/d96d4766-6612-414d-bf5e-0c043a3f30c3.img\n\t\t\t--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/\n\t\t\t--appdir=/apps/application/\n\t\t\t--worker_in_master_cpus=12\n\t\t\t--worker_in_master_memory=24000\n\t\t\t--worker_working_dir=/home_nfs/home_garciad\n\t\t\t--lang=c\n\t\t\t--monitoring=1000 -d /apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_garciad/demo_test/cpu_gpu_run_data\n \nTemp submit script is: /tmp/tmp.y7WxtgjPSz\nRequesting 2 processes\nSubmitted batch job 3357\n'

		sbatch_id = executor.__extract_id_from_sigularity_pm_app__(output)

		self.assertEquals(3357, sbatch_id)

		output = b'COMPSS_HOME=/home_nfs/home_ejarquej/installations/rc1707/COMPSs\nSC Configuration:          nova.cfg\nQueue:                     default\nReservation:               disabled\nNum Nodes:                 1\nNum Switches:              0\nGPUs per node:             2\nJob dependency:            None\nExec-Time:                 00:10:00\nStorage Home:              null\nStorage Properties:        \nOther:                     --sc_cfg=nova.cfg\n\t\t\t--gpus_per_node=2\n\t\t\t--cpus_per_node=12\n\t\t\t--container_image=/tmp/d96d4766-6612-414d-bf5e-0c043a3f30c3.img\n\t\t\t--container_compss_path=/opt/TANGO/TANGO_ProgrammingModel/COMPSs/\n\t\t\t--appdir=/apps/application/\n\t\t\t--worker_in_master_cpus=12\n\t\t\t--worker_in_master_memory=24000\n\t\t\t--worker_working_dir=/home_nfs/home_garciad\n\t\t\t--lang=c\n\t\t\t--monitoring=1000 -d /apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_garciad/demo_test/cpu_gpu_run_data\n \nTemp submit script is: /tmp/tmp.y7WxtgjPSz\nRequesting 2 processes\nSubmitted batch job     3357    \n\n\n'

		sbatch_id = executor.__extract_id_from_sigularity_pm_app__(output)

		self.assertEquals(3357, sbatch_id)

	@mock.patch("shell.execute_command")
	def test_execute_application_type_slurm_sbatch(self, mock_shell):
		"""
		It verifies that the application type slurm sbatch is executed
		"""

		# First we verify that the testbed is of type SLURM to be able
		# to execute it, in this case it should give an error since it is
		# not of type slurm

		# We define the different entities necessaryb for the test.
		testbed = Testbed(name="nova2",
						  on_line=True,
						  category="xxxx",
						  protocol="SSH",
						  endpoint="user@testbed.com",
						  package_formats= ['sbatch', 'SINGULARITY'],
						  extra_config= {
						  	"enqueue_compss_sc_cfg": "nova.cfg" ,
						  	"enqueue_env_file": "/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv"
						  })
		db.session.add(testbed)

		application = Application(name="super_app")
		db.session.add(application)
		db.session.commit() # So application and testbed get an id

		executable = Executable()
		executable.compilation_type = "SLURM:SBATCH"
		executable.executable_file = "pepito.sh"
		db.session.add(executable)
		db.session.commit() # We do this so executable gets and id

		deployment = Deployment()
		deployment.testbed_id = testbed.id
		deployment.executable_id = executable.id
		db.session.add(deployment) # We add the executable to the db so it has an id

		execution_config = ExecutionConfiguration()
		execution_config.execution_type = "SLURM:SBATCH"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		db.session.add(execution_config)
		db.session.commit()

		execution = Execution("SLURM:SBATCH", executor.execute_status_submitted)

		executor.execute_application_type_slurm_sbatch(execution, execution_config.id)

		self.assertEquals("SLURM:SBATCH", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed does not support SLURM:SBATCH applications", execution.output)

		# If the testbed is off-line, execution isn't allowed also
		testbed.category = Testbed.slurm_category
		testbed.on_line = False
		db.session.commit()

		execution.status = executor.execute_status_submitted

		execution = Execution("SLURM:SBATCH", executor.execute_status_submitted)

		executor.execute_application_type_slurm_sbatch(execution, execution_config.id)

		self.assertEquals("SLURM:SBATCH", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed is off-line", execution.output)

		## Test executing
		output = b'Submitted batch job 5740'
		mock_shell.return_value = output

		testbed.category = Testbed.slurm_category
		testbed.on_line = True
		db.session.commit()

		execution.status = executor.execute_status_submitted

		execution = Execution("SLURM:SBATCH", executor.execute_status_submitted)

		executor.execute_application_type_slurm_sbatch(execution, execution_config.id)

		mock_shell.assert_called_with("sbatch",
									  "user@testbed.com",
									  [
									  	"pepito.sh"
									   ]
									  )
		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()
		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(5740, execution.slurm_sbatch_id)

	@mock.patch("executor.monitor_execution_singularity_apps")
	def test_monitor_execution_apps(self, mock_monitor):
		"""
		It verifies that the method that monitors the execution of apps
		works as expected
		"""

		execution_1 = Execution("typeX", Execution.__status_running__)
		execution_2 = Execution(Executable.__type_singularity_pm__, Execution.__status_finished__)
		execution_3 = Execution(Executable.__type_singularity_pm__, Execution.__status_running__)

		mock_monitor.return_value = 'pepito'

		db.session.add(execution_1)
		db.session.add(execution_2)
		db.session.add(execution_3)
		db.session.commit()

		executor.monitor_execution_apps()
		mock_monitor.assert_called_with(execution_3)

		self.assertEquals('pepito', execution_3.status)


	@mock.patch("executor._parse_sacct_output")
	def test_monitor_execution_singularity_apps(self, mock_parse):
		"""
		It checks that the monitoring of singularity apps 
		is working
		"""

		execution = Execution("typeX", "xxx")
		execution.slurm_sbatch_id = 1
		execution_configuration = ExecutionConfiguration()
		execution.execution_configuration=execution_configuration
		testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])
		execution_configuration.testbed=testbed

		mock_parse.return_value = '?'

		status = executor.monitor_execution_singularity_apps(execution)

		self.assertEquals("xxx", status)

		mock_parse.return_value = 'RUNNING'

		status = executor.monitor_execution_singularity_apps(execution)

		self.assertEquals("RUNNING", status)

		call_1 = call(1,"user@server")
		call_2 = call(1,"user@server")
		calls = [ call_1, call_2, ]
		mock_parse.assert_has_calls(calls)

	@mock.patch("shell.execute_command")
	def test_parse_sacct_output(self, mock_shell):
		"""
		It checks that the monitoring of singularity apps 
		is working

		Command to be executed:

		[garciad@ns54 ~]$ sacct -j 4340 -o JobID,NNodes,State,ExitCode,DerivedExitcode,Comment
		JobID   NNodes      State ExitCode DerivedExitCode        Comment 
		------------ -------- ---------- -------- --------------- -------------- 
		4340                1  COMPLETED      0:0             1:0                
		4340.batch          1  COMPLETED      0:0                                
		4340.0              1  COMPLETED      0:0                                
		4340.1              1     FAILED      1:0 
		"""

		# TEST NO OUTPUT
		output = b'       JobID   NNodes      State ExitCode DerivedExitCode        Comment \n------------ -------- ---------- -------- --------------- -------------- '

		mock_shell.return_value = output

		status = executor._parse_sacct_output(4340, 'test@pepito.com')

		self.assertEquals('?', status)

		# TEST RUNNING
		output = b'       JobID   NNodes      State ExitCode DerivedExitCode        Comment \n------------ -------- ---------- -------- --------------- -------------- \n4340                1  RUNNING      0:0             0:0                \n4340.batch          1  COMPLETED      0:0                                \n4340.0              1  COMPLETED      0:0                                \n4340.1              1     COMPLETED      0:0 '
		mock_shell.return_value = output

		status = executor._parse_sacct_output(4340, 'test@pepito.com')

		self.assertEquals('RUNNING', status)

		# TEST COMPLETED
		output = b'       JobID   NNodes      State ExitCode DerivedExitCode        Comment \n------------ -------- ---------- -------- --------------- -------------- \n4340                1  COMPLETED      0:0             0:0                \n4340.batch          1  COMPLETED      0:0                                \n4340.0              1  COMPLETED      0:0                                \n4340.1              1     COMPLETED      0:0 '

		mock_shell.return_value = output

		status = executor._parse_sacct_output(4340, 'test@pepito.com')

		self.assertEquals('COMPLETED', status)

		# TEST FAILED
		output = b'       JobID   NNodes      State ExitCode DerivedExitCode        Comment \n------------ -------- ---------- -------- --------------- -------------- \n4340                1  COMPLETED      0:0             1:0                \n4340.batch          1  COMPLETED      0:0                                \n4340.0              1  COMPLETED      0:0                                \n4340.1              1     FAILED      1:0 '

		mock_shell.return_value = output

		status = executor._parse_sacct_output(4340, 'test@pepito.com')

		self.assertEquals('FAILED', status)

		# TEST UNKNOWN
		output = b'       JobID   NNodes      State ExitCode DerivedExitCode        Comment \n------------ -------- ---------- -------- --------------- -------------- \n4340                1  UNKNOWN      0:0             1:0                \n4340.batch          1  UNKNOWN      0:0                                \n4340.0              1  UNKNOWN      0:0                                \n4340.1              1     UNKNOWN      1:0 '

		mock_shell.return_value = output

		status = executor._parse_sacct_output(4340, 'test@pepito.com')

		self.assertEquals('UNKNOWN', status)

		call_1 = call('sacct', server='test@pepito.com', params=['-j', 4340, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
		call_2 = call('sacct', server='test@pepito.com', params=['-j', 4340, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
		call_3 = call('sacct', server='test@pepito.com', params=['-j', 4340, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
		call_4 = call('sacct', server='test@pepito.com', params=['-j', 4340, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
		call_5 = call('sacct', server='test@pepito.com', params=['-j', 4340, '-o', 'JobID,NNodes,State,ExitCode,DerivedExitcode,Comment'])
		calls = [ call_1, call_2, call_3, call_4, call_5]
		mock_shell.assert_has_calls(calls)

	def test__extract_id_from_squeue__(self):
		"""
		Test that it is possible to extract the id from the first squeue output
		"""

		# example output
		output = b'             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)\n              4610       all singular  garciad  R       0:01      2 ns[55-56]\n'

		squeue_id = executor.__extract_id_from_squeue__(output)

		self.assertEquals(4610, squeue_id)

	@mock.patch("shell.execute_command")
	def test_execute_application_type_singularity_srun(self, mock_shell):
		"""
		Test the correct work fo this function
		"""

		# We define the different entities necessaryb for the test.
		testbed = Testbed(name="nova2",
						  on_line=True,
						  category="SLURM",
						  protocol="SSH",
						  endpoint="user@testbed.com",
						  package_formats= ['sbatch', 'SINGULARITY'],
						  extra_config= {
						  	"enqueue_compss_sc_cfg": "nova.cfg" ,
						  	"enqueue_env_file": "/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv"
						  })
		db.session.add(testbed)

		application = Application(name="super_app")
		db.session.add(application)
		db.session.commit() # So application and testbed get an id

		executable = Executable()
		executable.source_code_file = 'test.zip'
		executable.compilation_script = 'gcc -X'
		executable.compilation_type = "SINGULARITY:SRUN"
		executable.singularity_app_folder="/singularity/app/folder"
		executable.singularity_image_file="pepito.img"
		executable.status = "COMPILED"
		executable.application = application
		db.session.add(executable)
		db.session.commit() # We do this so executable gets and id

		deployment = Deployment()
		deployment.testbed_id = testbed.id
		deployment.executable_id = executable.id
		deployment.path="/pepito/pepito.img"
		db.session.add(deployment) # We add the executable to the db so it has an id

		execution_config = ExecutionConfiguration()
		execution_config.execution_type ="SINGULARITY:SRUN"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		execution_config.num_nodes = 2
		#execution_config.num_gpus_per_node = 2
		execution_config.num_cpus_per_node = 16
		execution_config.exec_time = 10 
		execution_config.command = "/apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_ejarquej/demo_test/cpu_gpu_run_data"
		execution_config.compss_config = "--worker_in_master_cpus=12 --worker_in_master_memory=24000 --worker_working_dir=/home_nfs/home_ejarquej --lang=c --monitoring=1000 -d"
		db.session.add(execution_config)
		db.session.commit()

		output = b'             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)\n              4610       all singular  garciad  R       0:01      2 ns[55-56]\n'

		mock_shell.return_value = output

		# TEST starts here:
		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_singularity_srun(execution, execution_config.id)

		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()

		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(4610, execution.slurm_sbatch_id)

		call_1 = call('(', "user@testbed.com",
									  [
									  	"srun",
									  	"-N",
									  	"2",
									  	"-n",
									  	"16",
									  	"singularity",
									  	"run",
									  	"/pepito/pepito.img",
									  	">",
										"allout.txt",
										"2>&1",
									  	"&",
									  	")",
									  	";",
									  	"sleep",
									  	"1;",
									  	"squeue"
									   ])

		# adding a new type of execution
		execution_config = ExecutionConfiguration()
		execution_config.execution_type ="SINGULARITY:SRUN"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		execution_config.num_gpus_per_node = 2
		execution_config.num_cpus_per_node = 16
		execution_config.exec_time = 10 
		execution_config.command = "/apps/application/master/Matmul 2 1024 12.34 /home_nfs/home_ejarquej/demo_test/cpu_gpu_run_data"
		execution_config.compss_config = "--worker_in_master_cpus=12 --worker_in_master_memory=24000 --worker_working_dir=/home_nfs/home_ejarquej --lang=c --monitoring=1000 -d"
		db.session.add(execution_config)
		db.session.commit()

		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_singularity_srun(execution, execution_config.id)

		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()

		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(4610, execution.slurm_sbatch_id)

		call_2 = call('(', "user@testbed.com",
									  [
									  	"srun",
									  	"--gres=gpu:2",
									  	"-n",
									  	"16",
									  	"singularity",
									  	"run",
									  	"/pepito/pepito.img",
									  	">",
										"allout.txt",
										"2>&1",
									  	"&",
									  	")",
									  	";",
									  	"sleep",
									  	"1;",
									  	"squeue"
									   ])
		calls = [ call_1, call_2]
		mock_shell.assert_has_calls(calls)

	@mock.patch("shell.execute_command")
	def test_execute_application_type_slurm_srun(self, mock_shell):
		"""
		Test the correct work fo this function
		"""

		# We define the different entities necessaryb for the test.
		testbed = Testbed(name="nova2",
						  on_line=True,
						  category="SLURM",
						  protocol="SSH",
						  endpoint="user@testbed.com",
						  package_formats= ['sbatch', 'srun', 'SINGULARITY'],
						  extra_config= {
						  	"enqueue_compss_sc_cfg": "nova.cfg" ,
						  	"enqueue_env_file": "/home_nfs/home_ejarquej/installations/rc1707/COMPSs/compssenv"
						  })
		db.session.add(testbed)

		application = Application(name="super_app")
		db.session.add(application)
		db.session.commit() # So application and testbed get an id

		executable = Executable()
		executable.source_code_file = 'test.zip'
		executable.compilation_script = 'gcc -X'
		executable.compilation_type = "SLURM:SRUN"
		executable.executable_file = "/usr/local/gromacs-4.6.7-cuda2/bin/mdrun"
		executable.status = "COMPILED"
		executable.application = application
		db.session.add(executable)
		db.session.commit() # We do this so executable gets and id

		deployment = Deployment()
		deployment.testbed_id = testbed.id
		deployment.executable_id = executable.id
		db.session.add(deployment) # We add the executable to the db so it has an id

		execution_config = ExecutionConfiguration()
		execution_config.execution_type ="SLURM:SRUN"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		execution_config.num_nodes = 2
		#execution_config.num_gpus_per_node = 2
		execution_config.num_cpus_per_node = 16
		execution_config.srun_config = "--job-name gromacstest --profile=energy,task --acctg-freq=Energy=1,Task=1"
		execution_config.command = "-s /home_nfs/home_dineshkr/Gromacs/gromacs-run/peptide_water_3k.tpr -v -nsteps 50000 -testverlet"
		db.session.add(execution_config)
		db.session.commit()

		output = b'             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)\n              4610       all singular  garciad  R       0:01      2 ns[55-56]\n'

		mock_shell.return_value = output

		# TEST starts here:
		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_slurm_srun(execution, execution_config.id)

		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()

		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(4610, execution.slurm_sbatch_id)

		call_1 = call('(', "user@testbed.com",
									  [
									  	'srun', 
									  	'-N', 
									  	'2', 
									  	'-n', 
									  	'16', 
									  	'--job-name gromacstest --profile=energy,task --acctg-freq=Energy=1,Task=1', 
									  	'/usr/local/gromacs-4.6.7-cuda2/bin/mdrun', 
									  	'-s /home_nfs/home_dineshkr/Gromacs/gromacs-run/peptide_water_3k.tpr -v -nsteps 50000 -testverlet',							  	
									  	">",
										"allout.txt",
										"2>&1",
									  	"&",
									  	")",
									  	";",
									  	"sleep",
									  	"1;",
									  	"squeue"
									   ])

		# adding a new type of execution
		execution_config = ExecutionConfiguration()
		execution_config.execution_type ="SLURM:SRUN"
		execution_config.application = application
		execution_config.testbed = testbed
		execution_config.executable = executable 
		execution_config.num_nodes = 2
		execution_config.num_gpus_per_node = 2
		execution_config.num_cpus_per_node = 16
		execution_config.srun_config = "--job-name gromacstest --profile=energy,task --acctg-freq=Energy=1,Task=1"
		execution_config.command = "-s /home_nfs/home_dineshkr/Gromacs/gromacs-run/peptide_water_3k.tpr -v -nsteps 50000 -testverlet"
		db.session.add(execution_config)
		db.session.commit()

		execution = Execution(execution_config.execution_type,
						  executor.execute_status_submitted)
		executor.execute_application_type_slurm_srun(execution, execution_config.id)

		execution = db.session.query(Execution).filter_by(execution_configuration_id=execution_config.id).first()

		self.assertEquals(execution.execution_type, execution_config.execution_type)
		self.assertEquals(execution.status, Execution.__status_running__)
		self.assertEquals(4610, execution.slurm_sbatch_id)

		call_2 = call('(', "user@testbed.com",
									  [
									  	'srun', 
									  	'-N', 
									  	'2',
									  	"--gres=gpu:2", 
									  	'-n', 
									  	'16', 
									  	'--job-name gromacstest --profile=energy,task --acctg-freq=Energy=1,Task=1', 
									  	'/usr/local/gromacs-4.6.7-cuda2/bin/mdrun', 
									  	'-s /home_nfs/home_dineshkr/Gromacs/gromacs-run/peptide_water_3k.tpr -v -nsteps 50000 -testverlet',							  	
									  	">",
										"allout.txt",
										"2>&1",
									  	"&",
									  	")",
									  	";",
									  	"sleep",
									  	"1;",
									  	"squeue"
									   ])
		calls = [ call_1, call_2]
		mock_shell.assert_has_calls(calls)

	@mock.patch("shell.execute_command")
	def test_cancel_execution(self, mock_shell):
		"""
		It test the correct work of the cancel execution method
		"""

		# We create the execution objects to test
		execution_1 = Execution(Executable.__type_singularity_srun__,
						  Execution.__status_running__)
		execution_1.slurm_sbatch_id = 1
		execution_2 = Execution(Executable.__type_singularity_pm__,
						  Execution.__status_running__)
		execution_2.slurm_sbatch_id = 2
		execution_3 = Execution("other_type",
						  Execution.__status_running__)
		execution_3.slurm_sbatch_id = 3
		execution_4 = Execution(Executable.__type_singularity_srun__,
						  Execution.__status_finished__)
		execution_4.slurm_sbatch_id = 4

		executor.cancel_execution(execution_1, "user@testbed.com")
		executor.cancel_execution(execution_2, "user@testbed.com")
		executor.cancel_execution(execution_3, "user@testbed.com")
		executor.cancel_execution(execution_4, "user@testbed.com")

		call_1 = call("scancel", "user@testbed.com", [ "1" ])
		call_2 = call("scancel", "user@testbed.com", [ "2" ])
		calls = [ call_1, call_2]
		mock_shell.assert_has_calls(calls)

	@mock.patch('executor.find_first_node')
	@mock.patch("shell.execute_command")
	def test_add_resource(self, mock_shell, mock_find_node):
		"""
		It tests that it is possible to add a resource
		"""

		l = LogCapture() # we cature the logger

		# Sub test 1 - Wrong type of Execution
		execution = Execution("pepito", Execution.__status_running__)
		executor.add_resource(execution)

		# Sub test 2 - Execution not running in right state
		execution = Execution(Executable.__type_singularity_pm__, Execution.__status_failed__)
		executor.add_resource(execution)

		# Sub test 3 - Execution should get a new resource
		execution = Execution(Executable.__type_singularity_pm__, Execution.__status_running__)
		executable = Executable()
		executable.singularity_image_file = "image_file"

		execution_configuration = ExecutionConfiguration()
		execution_configuration.executable = executable

		testbed = Testbed( "testbed", True, "nice_testbed", "ssh", "endpoint")

		execution_configuration.testbed = testbed
		execution.execution_configuration = execution_configuration
		execution.slurm_sbatch_id = 21

		mock_find_node.return_value = 'ns31'

		executor.add_resource(execution)

		call_1 = call("adapt_compss_resources", "endpoint", [ 'ns31', 21, 'CREATE SLURM-Cluster default', "image_file" ])
		calls = [ call_1 ]
		mock_shell.assert_has_calls(calls)
		
		# Checking that we are logging the correct message
		l.check(
			('root', 'INFO', 'Execution: pepito it is not compatible with add resource action'),
			('root', 'INFO', 'Executing type corresponds with SINGULARITY_PM, trying adaptation'),
			('root', 'INFO', 'Execution is not in RUNNING status, no action can be done'),
			('root', 'INFO', 'Executing type corresponds with SINGULARITY_PM, trying adaptation'),
		)
		l.uninstall() # We uninstall the capture of the logger

    
	@mock.patch("shell.execute_command")
	def test_find_first_node(self, mock_shell):
		"""
		Verifies that it is possible to find the first node under this outputs:
		"""

		# Sub Test 1
		output = b'NODELIST\nns51\n'
		mock_shell.return_value = output

		node = executor.find_first_node(22, 'endpoint')
		self.assertEquals(node, 'ns51')

		# Sub Test 2
		output = b'NODELIST\n   ns51      \n'
		mock_shell.return_value = output

		node = executor.find_first_node(22, 'endpoint')
		self.assertEquals(node, 'ns51')

		# Sub Test 3
		output = b'NODELIST\n   ns[55-60]      \n'
		mock_shell.return_value = output

		node = executor.find_first_node(22, 'endpoint')
		self.assertEquals(node, 'ns55')

		# Sub Test 4
		output = b'NODELIST\n   ns[53-60],ns34      \n'
		mock_shell.return_value = output

		node = executor.find_first_node(22, 'endpoint')
		self.assertEquals(node, 'ns53')

		call_1 = call("squeue", "endpoint", [ '-j', 22, '-o', '%N' ])
		call_2 = call("squeue", "endpoint", [ '-j', 22, '-o', '%N' ])
		call_3 = call("squeue", "endpoint", [ '-j', 22, '-o', '%N' ])
		call_4 = call("squeue", "endpoint", [ '-j', 22, '-o', '%N' ])
		calls = [ call_1, call_2, call_3, call_4 ]
		mock_shell.assert_has_calls(calls)

