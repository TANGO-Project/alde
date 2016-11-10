# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

class Testbed():
    """Object model of the testbed connected to the Application Lifececyle
       Deployment engine"""

    def __init__(self, name, on_line, category, protocol, endpoint, package_formats):
        """Initialize the basis attributes for the testbed class"""

        self.name = name
        self.on_line = on_line
        self.category = categoy
        self.protocol = protocol
        sefl.package_formats = package_formats
        
