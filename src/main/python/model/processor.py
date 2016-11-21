# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


class Processor():
    """This class represents the basic information for all types of processors.
       From CPU, FPGA, GPUs... etc..."""

    def __init__(self, vendor_id, model_name):
        """Initialize the basic attributes of the class"""

        self.vendor_id = vendor_id
        self.model_name = model_name


class CPU(Processor):
    """This class represents the basic information of a CPU"""

    def __init__(self, vendor_id, model_name, arch, model, cpu_speed, fpu, cpu_cores, cache, flags):
        """Initialize the basic attributes of a CPU"""

        super().__init__(vendor_id, model_name)
        self.arch = arch
        self.model = model
        self.cpu_speed = cpu_speed
        self.fpu = fpu
        self.cpu_cores = cpu_cores
        self.cache = cache
        self.flags = flags
