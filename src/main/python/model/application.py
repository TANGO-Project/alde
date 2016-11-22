# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

class Application():
    """
    Object that represents all the information for an
    application that it needs to be build and maybe deploy by the
    Application Lifecycle Deployment Engine
    """

    def __init__(self, name, path_to_code):
        """Initializes the basic parameters of the class"""

        self.name = name
        self.path_to_code = path_to_code
        self.build = Build("","")
        self.package = []
        self.executable = []
        self.execution = Execution("","")


class Build():
    """
    Object that represents all the building information for an
    application that needs to be build for one or more different
    targetted architectures
    """

    def __init__(self, script, params):
        """Initialize the basic parameters of the class"""

        self.script = script
        self.params = params

class Execution():
    """
    Object that represents all the configuration an application have for
    being executed into different types of infrastructures
    """

    def __init__(self, command, params):
        """Initializes the basic parameters of the class"""

        self.command = command
        self.params = params
