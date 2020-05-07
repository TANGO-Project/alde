#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.gnu.org/licenses/agpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Module that has all the logic to talk with SLURM
#

import re
import shell
import copy
import query
import logging
import linux_probes.cpu_info_parser as parser
import inventory
from models import db, Testbed, Node, CPU, GPU, Memory

import testbeds.common
from testbeds.constants import NAME
from testbeds.constants import MEMORY
from testbeds.constants import STATE
from testbeds.constants import GRES


def is_node_idle(nodes, node_name):
    """
    For a list of nodes checks if the nodle is idle
    """
    node = next(filter(lambda node: node[NAME] == node_name, nodes), None)
    
    if node and node['partition_state'] == 'idle' :
        return True
    else :
        return False


def parse_sinfo_partitions(command_output):
    """
    It parses an text in the following format:
    PARTITION    AVAIL  TIMELIMIT  NODES  STATE NODELIST
    bullx           up   infinite      1  drain nd15
    bullx           up   infinite      9   idle nd[10-14,16-19]

    into a list with a struct per node
    """

    nodes = []
    lines = command_output.decode('utf-8').split('\n')

    for line in lines:

        if not line.startswith("PARTITION") and line:
            line = re.sub(' +', ' ', line)
            words = line.split(' ')

            partition = words[0]
            avail = words[1]
            timelimit = words[2]
            state = words[4]
            nodes_string = words[5]

            if '[' not in nodes_string:
                node = { 'partition': partition,
                         'partition_avail': avail,
                         'partition_timelimit': timelimit,
                         'partition_state': state,
                         NAME: nodes_string}

                nodes.append(node)

            else:
                node_start_name = nodes_string.split('[')[0]
                boundaries = nodes_string.split('[')[1].split(']')[0].split(',')
                for boundarie in boundaries:
                    if '-' not in boundarie:
                        node_name = node_start_name + boundarie
                        node = { 'partition': partition,
                                 'partition_avail': avail,
                                 'partition_timelimit': timelimit,
                                 'partition_state': state,
                                 NAME: node_name}

                        nodes.append(node)
                    else:
                        limits = boundarie.split('-')
                        start = int(limits[0])
                        end = int(limits[1]) + 1

                        for number in range(start,end):
                            node_name = node_start_name + str(number)
                            node = { 'partition': partition,
                                     'partition_avail': avail,
                                     'partition_timelimit': timelimit,
                                     'partition_state': state,
                                     NAME: node_name}

                            nodes.append(node)

    return nodes


def get_nodes_testbed(testbed):
    """
    This function gets the testbed object information, from that information
    it determines if the testbed it is of the category SLURM.

    If it is SLURM, it will determine if it connects via ssh.

        If it connects via ssh it will get the node info executing the command
        via ssh

        If it is not ssh, it will execute directly the sinfo command in console.

    If it is not type SLURM it will just return an empty list
    """
    command = "sinfo"
    params = ["-a"]

    return testbeds.common.get_nodes_testbed(testbed, command, params, parse_sinfo_partitions)


def check_nodes_in_db_for_on_line_testbeds():
    """
    This function it is going to get all the nodes in the db that are:
        on-line
        Type slurm

    To each node it is going to get the nodes and it is going to compare the
    information with the information in the db. It can happen two things:
        * If the node is in the db, info it is updated if necessary
        * If the node is not in the db, it is added

    After that, the method it is going to verify if there is a node that it is
    in the db but it is not in the list provided. If that happens, the node
    it is changed to dissabled
    """
    #
    # This function is obsolete and is here just to make existing tests pass.
    # Application code MUST NOT call this function, 
    # but testbeds.facade.check_nodes_in_db_for_on_line_testbeds
    #
    import testbeds.facade
    tbs = query.get_online_testbeds(Testbed.slurm_category)

    for testbed in tbs:
        testbeds.facade.check_testbed_nodes_in_db(testbed)


def parse_scontrol_information(command_output):
    """
    This function will parse all info of the command
    scontrol -o  --all show node

    This will be used to get information and live stats of the status_code
    of the node
    """
    def normalize(node):
        if 'NodeName' in node:
            node[NAME] = node['NodeName']
        if 'State' in node:
            node[STATE] = node['State']
        if 'RealMemory' in node:
            node[MEMORY] = node['RealMemory']
        if 'Gres' in node:
            node[GRES] = node['Gres']

    nodes_info = []
    lines = command_output.decode('utf-8').split('\n')

    r = re.compile(r'(\w+)=([^=]+\s|$)')
    for line in lines:
        new_dict = {}
        for k,v in r.findall(line):
            new_dict[k] = v.strip()
        normalize(new_dict)
        nodes_info.append(new_dict)

    return nodes_info


def  update_cpu_node_information():
    """
    This method updates the CPU information of nodes in case of
    on-line SLURM testbeds.

    It is going to try to ssh into the node, if the node is enabled, if an
    error occours it keeps the node information as it is. If no error occours
    updates the entries in the db deleting the old CPU information first.
    """
    #
    # This function is obsolete and is here just to make existing tests pass.
    # Application code MUST NOT call this function, 
    # but testbeds.facade.update_testbed_cpu_node_information()
    #
    import testbeds.facade
    
    tbs = query.get_slurm_online_testbeds()

    for testbed in tbs:
        testbeds.facade.update_testbed_cpu_node_information(testbed)


def get_node_information(testbed):
    """
    This function gets the nodes object information, from that information
    it determines if the testbed it is of the category SLURM.

    If it is SLURM, it will determine if it connects via ssh.

        If it connects via ssh it will get the node info executing the command
        via ssh

        If it is not ssh, it will execute directly the sinfo command in console.

    If it is not type SLURM it will just return an empty list

    The command to be executed is:

    scontrol -o  --all show node
    """
    command = "scontrol"
    params = ["-o", "--all", "show", "node"]
    return testbeds.common.get_nodes_testbed(testbed, command, params, parse_scontrol_information)


def update_node_information():
    """
    This function gets all the testbed that are SLURM and have been
    configured to retrieve all information automatically and
    update the node information if necessary
    """
    #
    # This function is obsolete and is here just to make existing test pass
    # Application code MUST NOT call this function, 
    # but testbeds.facade.update_node_information()
    #
    import testbeds.facade

    tbs = query.get_slurm_online_testbeds()

    for testbed in tbs:
        testbeds.facade.update_testbed_node_information(testbed)


def parse_memory(memory: str) -> Memory:
    return Memory(size=memory, units=Memory.MEGABYTE)


def parse_gre_field_info(gre):
    """
    This function will parse the GRE field of the scontrol output to know
    if this specific node of slurm has any kind of special hardware attached
    to it such as GPUs, Xeon Phis, etc...

    gre field has format like this: gpu:tesla2050:2,bandwidth:lustre:no_consume:4G

    This function will return a dictionary with the relevant information
    """

    resources = {}

    for resource in gre.split(','):

        resource_info = resource.split(':')

        if resource_info[0] == 'gpu':
            gpu_model = inventory.find_gpu_slurm(resource_info[1])

            if gpu_model:

                if 'gpu' in resources:
                    gpus = resources['gpu']
                else:
                    gpus = []

                if len(resource_info) == 3:
                    for i in range(int(resource_info[2])):
                        gpus.append(copy.deepcopy(gpu_model))
                else:
                    gpus.append(gpu_model)

                resources['gpu'] = gpus

    return resources

def execute_srun(testbed, execution_configuration, executable, deployment, singularity=False):
    """
    This will execute an slurm application and return the output
    """

	# Preparing the command to be executed
    command = "' ("
    endpoint = testbed.endpoint
    params = []
    params.append("srun")
    if execution_configuration.num_nodes:
        params.append("-N")
        params.append(str(execution_configuration.num_nodes))
    if execution_configuration.num_gpus_per_node:
        params.append("--gres=gpu:" + str(execution_configuration.num_gpus_per_node))
    params.append("-n")
    params.append(str(execution_configuration.num_cpus_per_node))
    if execution_configuration.srun_config:
        params.append(execution_configuration.srun_config)
    if singularity :
        params.append('singularity')
        params.append('run')
        params.append(deployment.path)
    else :
        params.append(executable.executable_file)
        params.append(execution_configuration.command)
    params.append(">")
    params.append("allout.txt")
    params.append("2>&1")
    params.append("&")
    params.append(")")
    params.append(";")
    params.append("sleep")
    params.append("1;")
    params.append("squeue")
    params.append("'")
    
    logging.info("Launching execution of application: command: " + command + " | endpoint: " + endpoint + " | params: " + str(params))
    
    output = shell.execute_command(command, endpoint, params)
    
    return output

def stop_execution(execution_id, endpoint):
    """
    This will use scontrol to stop an execution

    scontrol suspend 7993
    """

    command="scontrol"
    params=["suspend", str(execution_id)]

    if endpoint:
        shell.execute_command(command=command, server=endpoint, params=params)
    else :
        shell.execute_command(command=command, params=params)