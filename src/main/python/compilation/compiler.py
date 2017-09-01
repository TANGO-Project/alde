# This module will compile the differe4nt applications
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from models import db, Executable
import shell
import uuid
import compilation.config as config

def return_not_compiled_executables():
	"""
	It looks in the db for all the not compiled executables
	"""

	return db.session.query(Executable).filter_by(status=Executable.__status_not_compiled__).all()

def compile_executables():
	"""
	From all the executables that in not compiled status it compiles one by one

	TODO in the future make this into threads since it could be more efficient,
	let the user configure the number of threads, since many apps compiling 
	at the same time could be problematic

	In bigger installation, it could be thinkable to create workers to
	perform this tasks.
	"""

	executables = return_not_compiled_executables()

	for executable in executables:
		if  executable.compilation_type == "SINGULARITY:PM":
			executable.status = Executable.__status_compiling__
			compile_singularity_pm(executable)
		else:
			executable.status = Executable.__status_error_type__

def compile_singularity_pm(executable):
	"""
	It compiles a singularity container of the type
	TANGO Programming Model
	"""

	# First we load the configuration config
	configuration = config.find_compilation_config('SINGULARITY:PM')

	# TODO Upload the file to the compilation VM
	#      - ssh into the VM and create a folder there
	#      - upload the zip file
	#      - unzip the zip file

	compilation_folder = create_random_folder(configuration['connection_url'])

	# TODO first we need to create the template, I need the parameters
	#      - create the new template
	#      - upload the template to the compiler VM
	#      - Register the tempalte into the db so it is stored for reference

	# TODO build the container
	#      - Build the container

	# TODO download the container and keep it in the db information
	#      - Download the containers (I need to determine where the container is)

	# TODO automate this process in the app configuration as a task

	pass

def create_random_folder(connection_url):
	"""
	It creates a random folder via ssh into a server and
	returns its localiton
	"""

	# We generate a UUID for the folder
	folder_name = str(uuid.uuid4())

	# We create the folder
	shell.execute_command('mkdir', connection_url, [ folder_name ])

	return folder_name