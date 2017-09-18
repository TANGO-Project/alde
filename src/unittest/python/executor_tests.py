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

class ExecutorTests(MappingTest):
	"""
	Unit test for the package Executor in charge of executing an application
	"""

	@mock.patch("shell.execute_command")
	@mock.patch("shell.scp_file")
	def test_upload_deployment(self, mock_scp, mock_execute):
		""" Verifies that the upload of the deployment works """

		executable = Executable("source", "script", "TYPE")
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable("source", "script", "SINGULARITY:PM")
		testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SBATCH" ] )

		executor.upload_deployment(executable, testbed)

		self.assertFalse(mock_scp.called)
		self.assertFalse(mock_execute.called)

		executable = Executable("source", "script", "SINGULARITY:PM")
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

	@mock.patch("executor.execute_application_type_singularity_pm")
	@mock.patch("executor.execute_application_type_slurm_sbatch")
	def test_execute_application(self, mock_slurm_sbatch, mock_singularity):
		"""
		Verifies that the right methods and status are set when an appplication is executed
		"""

		execution_configuration = ExecutionConfiguration()
		execution_configuration.execution_type = "slurm:sbatch"
		db.session.add(execution_configuration)
		db.session.commit()

		t = executor.execute_application(execution_configuration)

		execution = db.session.query(Execution).filter_by(execution_type="slurm:sbatch").first()
		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_slurm_sbatch.assert_called_with(execution)

		execution_configuration.execution_type = "SINGULARITY:PM"
		db.session.commit()

		t = executor.execute_application(execution_configuration)
		execution = db.session.query(Execution).filter_by(execution_type="SINGULARITY:PM").first()
		self.assertEquals("SINGULARITY:PM", execution.execution_type)
		self.assertEquals(executor.execute_status_submitted, execution.status)

		# We verify that the right method was called
		t.join()
		mock_singularity.assert_called_with(execution, execution_configuration.id)

		# We verify the wrong status of unrecognize execution type
		execution_configuration.execution_type = "xxx"
		db.session.commit()

		executor.execute_application(execution_configuration)

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

		executable = Executable(source_code_file="test.zip",
								compilation_script="gcc -X",
								compilation_type="SINGULARITY:PM",
								)
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

	def test_execute_application_type_slurm_sbatch(self):
		"""
		It verifies that the application type slurm sbatch is executed
		"""

		# First we verify that the testbed is of type SLURM to be able
		# to execute it, in this case it should give an error since it is
		# not of type slurm

		execution = Execution("slurm:sbatch", executor.execute_status_submitted)
		testbed = Testbed("name", True, "xxxx", "ssh", "user@server", ['slurm'])
		execution_configuration = ExecutionConfiguration()
		execution_configuration.execution_type = "slurm:sbatch"
		execution.execution_configuration=execution_configuration
		execution_configuration.testbed = testbed

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed does not support slurm:sbatch applications", execution.output)

		# If the testbed is off-line, execution isn't allowed also
		testbed.category = Testbed.slurm_category
		testbed.on_line = False
		execution.status = executor.execute_status_submitted

		executor.execute_application_type_slurm_sbatch(execution)

		self.assertEquals("slurm:sbatch", execution.execution_type)
		self.assertEquals(executor.execute_status_failed, execution.status)
		self.assertEquals("Testbed is off-line", execution.output)

	@mock.patch("executor.monitor_execution_singularity_apps")
	def test_monitor_execution_apps(self, mock_monitor):
		"""
		It verifies that the method that monitors the execution of apps
		works as expected
		"""

		execution_1 = Execution("typeX", Execution.__status_running__)
		execution_2 = Execution(Executable.__type_singularity_pm__, Execution.__status_finished__)
		execution_3 = Execution(Executable.__type_singularity_pm__, Execution.__status_running__)

		db.session.add(execution_1)
		db.session.add(execution_2)
		db.session.add(execution_3)
		db.session.commit()

		executor.monitor_execution_apps()
		mock_monitor.assert_called_with(execution_3)


	def test_monitor_execution_singularity_apps(self):
		"""
		It checks that the monitoring of singularity apps 
		is working
		"""

	

		# TODO

		output_squeue = b'             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)\n              3362       all   COMPSs  garciad  R       0:10      1 ns50'
		output_sacct = b'       JobID    JobName     MaxRSS    Elapsed \n------------ ---------- ---------- ---------- \n3362             COMPSs              00:00:10 \n3362.batch        batch      2308K   00:00:10 \n3362.0            mkdir      2796K   00:00:00 \n3362.1       singulari+      2792K   00:00:00 '

