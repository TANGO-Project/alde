# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

# class Application():
#
#
# class build():


class Execution():
    """
    Object that represents all the configuration an application have for
    being executed into different types of infrastructures
    """

    def __init__(self, command, params):
        """Initializes the basic parameters of the class"""

        self.command =command
        self.params = params
