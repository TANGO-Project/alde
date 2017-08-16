# This module will compile the differe4nt applications
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from models import db, Executable
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

	pass