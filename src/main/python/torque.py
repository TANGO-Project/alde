#
# Copyright 2020 Atos Research and Innovation
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
# This is being developed for the SODALITE Project: http://sodalite.eu
#

#
# Module that has all the logic to talk with TORQUE
#

import re
import shell
import copy
import query
import logging
import linux_probes.cpu_info_parser as parser
import inventory
import xmltodict
from models import db, Testbed, Node, CPU, GPU, Memory
from typing import Dict, List, Tuple

from testbeds.constants import NAME
from testbeds.constants import MEMORY
from testbeds.constants import STATE
from testbeds.constants import GRES

import testbeds.common


_NAME = "node_name"
_STATE = "state"
_STATUS = "status"
_PARSED_STATUS = "parsed_status"
_TOTAL_MEM = "totmem"


def get_nodes_testbed(testbed: Testbed) -> List[dict]:
    """
    This function gets the testbed object information, from that information
    it determines if the testbed it is of the category TORQUE.

    If it is TORQUE, it will determine if it connects via ssh.

        If it connects via ssh it will get the node info executing the command
        via ssh

        If it is not ssh, it will execute directly the sinfo command in console.

    If it is not type TORQUE it will just return an empty list
    """
    command = "pbsnodes"
    params = ["-x"]

    return testbeds.common.get_nodes_testbed(testbed, command, params, _parse_pbsnodes_information)


def _parse_pbsnodes_information(command_output):
    """
    This function will parse all info of the command
    `pbsnodes -x` and convert to a JSON structure 

    This will be used to get information and live stats of the status_code
    of the node
    """

    o = xmltodict.parse(command_output)
    nodes = o["Data"]["Node"]
    for n in nodes:
        status = _parse_status(n.get(_STATUS, ""))
        if status is not None:
            n[_PARSED_STATUS] = status
            n[MEMORY] = status[_TOTAL_MEM]
    return nodes


def _parse_status(statusline: str):
    """Parses different fields of the status line in the output of pbsnodes
    
    It returns a dictionary with all the parsed fields"""
    parts = ( i.split("=") for i in statusline.split(",") )
    return { part[0]: part[1] for part in parts }


def get_node_information(testbed: Testbed) -> List[Dict]:
    """Returns a list of dictionaries where each item list correspond to a node in the
    testbed. Dictionary keys must be normalized according to the constants defined in constants.py
    (e.g., the key for the node name is constants.NAME).

    The information is retrieved from the workload manager.
    """

    command = "pbsnodes"
    params = ["-x"]
    return testbeds.common.get_nodes_testbed(testbed, command, params, _parse_pbsnodes_information)


def parse_memory(memory: str) -> Memory:
    """Parses free text from pbsnodes.status output, returning [ size, unit ].
    On error, returns [0, Memory.MEGABYTE] """

    sizes = {
        "kb": Memory.KILOBYTE,
        "mb": Memory.MEGABYTE,
        "gb": Memory.GIGABYTE
    }

    try:
        for key in sizes.keys():
            if memory.endswith(key):
                size = int(memory[0:len(memory) - len(key)])
                unit = sizes[key]
                return Memory(size=size, units=unit)
    except ValueError:
        pass    # follows below

    return Memory(size=0, units=Memory.MEGABYTE)


def parse_gre_field_info(gre):
    """This function will return a dictionary with the GPU information
    """

    resources = {}

    # TODO! 

    return resources

