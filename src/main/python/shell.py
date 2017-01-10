#!/usr/bin/env python
# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

# SSH tools to execute commands

import subprocess

def _execute_command(command):
    """
    It just executes the give command and returns the output
    """
    output = subprocess.check_output(command)
    return output


def execute_command(command, server=''):
    """
    It executes a command, if server variable it is set, it will try to
    execute the command via ssh. It is not able to input user and password
    it is exected it is possible to connect to the server without it
    """

    if server != '':
        command = "ssh " + server + " \"" + command + "\""
        output = _execute_command(command)
    else:
        output = _execute_command(command)

    return output
