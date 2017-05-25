# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import unittest.mock as mock
import shell
import subprocess
from testfixtures import LogCapture

class ShellTests(unittest.TestCase):
    """
    Unittests for the functions of the shell file
    """

    @mock.patch('shell.subprocess')
    def test_non_ssh_command(self, mock_subprocess):
        """ test that a command is executed without using ssh """

        # We setup the mock
        mock_subprocess.check_output.return_value = "It is ok"

        output = shell.execute_command(command = "ls")

        # We verify this simple commands works
        self.assertEquals("It is ok", output)
        mock_subprocess.check_output.assert_called_with("ls")

        # We verify a more complex scenario with several params
        output = shell.execute_command(command = "ls", params=["-la", "."])
        # We verify that the params are passed in the correct way
        mock_subprocess.check_output.assert_called_with(["ls", "-la", "."])

    @mock.patch('shell.subprocess')
    def test_ssh_command(self, mock_subprocess):
        """
        Test that it is possible to exectue an ssh command if a server is given
        """

        shell.execute_command(command = "ls",
                              server="pepito@ssh.com",
                              params=["-la", "."])

        # We verify that the right params are passed to the mock_subprocess
        mock_subprocess.check_output.assert_called_with(["ssh",
                                                         "pepito@ssh.com",
                                                         "ls -la ."])

    @mock.patch('shell.subprocess.check_output')
    def test_raise_exception(self, mock_subprocess):
        """
        It verifies that an exception is raised when an error occours when
        exectuting a command, the exception will be handled latar own
        by the script that uses this function
        """

        l = LogCapture() # we cature the logger

        error = subprocess.CalledProcessError(returncode=255, cmd="ls")
        mock_subprocess.side_effect = error

        self.assertRaises(subprocess.CalledProcessError,
                          shell.execute_command,
                          command="ls",
                          params=["-la", "."])

        # Checking that we are logging the correct messages
        l.check(
            ('root', 'ERROR', "Trying to execute command: ['ls', '-la', '.']"),
            ('root', 'ERROR', "Error: Command 'ls' returned non-zero exit status 255"),
            ('root', 'ERROR', 'Trying to execute command at server ')
            )
        l.uninstall() # We uninstall the capture of the logger
