# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import shell

class ShellTests(unittest.TestCase):
    """
    Unittests for the functions of the shell file
    """

    def test_try(self):
        """ stupid for the moment"""

        output = shell.execute_command("ls")
        print(output)
        output = shell.execute_command(["ssh", "davidgp@davidgp.com \"date\""])
        #output = shell.execute_command("ls", "davidgp@davidgp.com")
        print(output)
