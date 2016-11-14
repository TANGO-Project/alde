# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

class Memory():
    """Object model of the RAM that can have a node in the Application
       Lifecycle Deployment Engine"""

    def __init__(self, size, units, address='', memory_type=''):
        """Initialize the basis attributes for the tetbed class"""

        self.memory_type = memory_type
        self.address = address
        self.size = size
        self.units = units
