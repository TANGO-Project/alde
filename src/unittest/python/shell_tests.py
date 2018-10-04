#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Unit tests that checks ALDE shell module
#

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
    def test_check_port_notation(self, mock_subprocess):
        """
        It checks taht we are parsing correctly the : for extracting the
        port and adding it as a parameter
        """

        shell.execute_command(command = "ls",
                              server="pepito@ssh.com:2222",
                              params=["-la", "."])

        # We verify that the right params are passed to the mock_subprocess
        mock_subprocess.check_output.assert_called_with(" ssh -p 2222 pepito@ssh.com ls -la .", shell=True)



    @mock.patch('shell.subprocess')
    def test_non_ssh_command(self, mock_subprocess):
        """ test that a command is executed without using ssh """

        # We setup the mock
        mock_subprocess.check_output.return_value = "It is ok"

        output = shell.execute_command(command = "ls")

        # We verify this simple commands works
        self.assertEquals("It is ok", output)
        mock_subprocess.check_output.assert_called_with("ls", shell=True)

        # We verify a more complex scenario with several params
        output = shell.execute_command(command = "ls", params=["-la", "."])
        # We verify that the params are passed in the correct way
        mock_subprocess.check_output.assert_called_with(" ls -la .", shell=True)

    @mock.patch('shell.subprocess')
    def test_ssh_command(self, mock_subprocess):
        """
        Test that it is possible to exectue an ssh command if a server is given
        """

        shell.execute_command(command = "ls",
                              server="pepito@ssh.com",
                              params=["-la", "."])

        # We verify that the right params are passed to the mock_subprocess
        mock_subprocess.check_output.assert_called_with(" ssh pepito@ssh.com ls -la .", shell=True)

    @mock.patch('shell.subprocess.check_output')
    def test_raise_exception(self, mock_subprocess):
        """
        It verifies that an exception is raised when an error occours when
        exectuting a command, the exception will be handled latar own
        by the script that uses this function
        """

        l = LogCapture() # we cature the logger

        error = subprocess.CalledProcessError(returncode=255, cmd="ls", output="failed")
        mock_subprocess.side_effect = error

        self.assertRaises(subprocess.CalledProcessError,
                          shell.execute_command,
                          command="ls",
                          params=["-la", "."])

        # Checking that we are logging the correct messages
        l.check(
            ('root', 'INFO', 'Executing: ls -la .'),
            ('root', 'ERROR', "Trying to execute command:  ls -la ."),
            ('root', 'ERROR', "Error: Command 'ls' returned non-zero exit status 255."),
            ('root', 'ERROR', "failed"),
            ('root', 'ERROR', 'Trying to execute command at server ')
            )
        l.uninstall() # We uninstall the capture of the logger

    @mock.patch('shell.subprocess')
    def test_scp_file(self, mock_subprocess):
        """
        Test that the command to scp a file is correctly done
        """

        shell.scp_file('/path/file', 'user@host', 'destination_path')

        # We verify that the right params are passed to the mock_subproces
        mock_subprocess.check_output.assert_called_with(' scp /path/file user@host:destination_path', shell=True)

        shell.scp_file('/path/file', 'user@host:5000', 'destination_path')

        # We verify that the right params are passed to the mock_subproces
        mock_subprocess.check_output.assert_called_with(' scp -P 5000 /path/file user@host:destination_path', shell=True)

        shell.scp_file('/path/file', 'user@host', 'destination_path', False)

        # We verify that the right params are passed to the mock_subproces
        mock_subprocess.check_output.assert_called_with(' scp user@host:destination_path /path/file', shell=True)