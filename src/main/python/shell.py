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
import logging

def _execute_command(command):
    """
    It just executes the give command and returns the output
    """

    try:
        output = subprocess.check_output(command)
        return output
    except subprocess.CalledProcessError as e:
        logging.error("Trying to execute command: " + str(command))
        logging.error('Error: %s', str(e))
        raise e

def execute_command(command, server='', params=[]):
    """
    It executes a command, if server variable it is set, it will try to
    execute the command via ssh. It is not able to input user and password
    it is exected it is possible to connect to the server without it
    """

    try:
        params.insert(0, command)

        if server != '':
            command = ""
            for param in params:
                command = command + " " + param

            params = []
            params.append('ssh')

            if ":" in server:
                connection = server.split(":")
                server = connection[0]
                port = connection[1]

                params.append('-p')
                params.append(port)

            params.append(server)

            command = command[1:]
            params.append(command)

        if len(params) == 1:
            output = _execute_command(params[0])
        else:
            output = _execute_command(params)

        return output

    except subprocess.CalledProcessError as e:
        logging.error("Trying to execute command at server " + server)
        raise e

def scp_file(local_filename, server, remote_filename='', upload=True):
    """
    It copies a file to a remote server. 
    The local_filename should be the complete path of the file
    """

    # Building the command
    params = []
    params.append('scp')

    if ":" in server:
        connection = server.split(":")
        server = connection[0]
        port = connection[1]

        params.append('-P')
        params.append(port)

    if upload :
        params.append(local_filename)
        params.append(server + ':' + remote_filename)
    else :
        params.append(server + ':' + remote_filename)
        params.append(local_filename)

    output = _execute_command(params)
