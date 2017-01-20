# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import itertools
import re
import shell
import subprocess
import logging
from model.models import CPU, Testbed, Node

architectures={ 'GenuineIntel': 'x86_64'}

def parse_cpu_info(cpu_info):
    """
    This class understands the file /proc/cpuinfo from linux distributions
    and parses it to extract information from it.

    This information is returned in the form of an array defined by the class
    models.cpu
    """

    lines = cpu_info.decode('utf-8')
    lines = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', lines, flags=re.M)
    lines = lines.split("\n")

    cpus = []

    for key,group in itertools.groupby(lines, lambda x: x==''):

        if not key:
            data={}
            for item in list(group):
                field,value=item.split(':')
                value=value.strip()
                data[field]=value

            cpu = CPU(vendor_id=data['vendor_id'],
                      model_name=data['model name'],
                      arch=architectures[data['vendor_id']],
                      model=data['model'],
                      speed=data['cpu MHz'],
                      fpu= data['fpu'] == 'yes',
                      cores=int(data['cpu cores']),
                      cache=data['cache size'],
                      flags=data['flags'])
            cpus.append(cpu)

    return cpus

def get_cpuinfo_node(testbed, node):
    """
    Given a testbed of type linux and a node, it is able to connect to it
    and retrieve the necessary information of the cpu_info of the node.

    In returns the cpu information in the form of a list of CPU objects
    """

    try:
        if node in testbed.nodes and not node.disabled:
            command = "ssh"
            params = [node.name, "'cat", "/proc/cpuinfo'"]

            if Testbed.protocol_local == testbed.protocol:
                cpu_info = shell.execute_command(command=command, params=params)
            elif Testbed.protocol_ssh == testbed.protocol:
                cpu_info = shell.execute_command(command=command,
                                                 server=testbed.endpoint,
                                                 params=params)
            else:
                logging.info("Tesbed protocol: %s not supported to get node information",
                    testbed.protocol)
                return []

            return parse_cpu_info(cpu_info)
        else:
            return []
    except subprocess.CalledProcessError:
        logging.error("Exception trying to get the node cpu info")
        return []
