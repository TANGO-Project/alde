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
# This file contains common business logic for all supported workload managers
#

import shell
from typing import List

from models import Testbed

def get_nodes_testbed(
    testbed: Testbed, 
    command: str,
    params: List[str],
    parse_func) -> List[dict]:

    """This function gets the list of nodes of a testbed, executing the given
    command+params according to the testbed protocol. 

    This function is intended to be called by the get_nodes_testbed of 
    a workload manager implementation
    """
    if testbed.protocol == Testbed.protocol_local:
        output = shell.execute_command(command=command, params=params)
    elif testbed.protocol == Testbed.protocol_ssh:
        output = shell.execute_command(command=command,
                                        server=testbed.endpoint,
                                        params=params)
    else:
        return []

    return parse_func(output)


def get_nodes_information(    
    testbed: Testbed, 
    command: str,
    params: List[str],
    parse_func) -> List[dict]:
    
    """Returns a list of dictionaries where each item list correspond to a node in the
    testbed. Dictionary keys must be normalized according to the constants defined in constants.py
    (e.g., the key for the node name is constants.NAME).

    The information is retrieved from the workload manager executing command + params.
    The output of the command is parsed and normalized by parse_func.

    This function is intended to be called by the get_nodes_testbed of 
    a workload manager implementation
    """

    if testbed.protocol == Testbed.protocol_local:
        output = shell.execute_command(command=command, params=params)
    elif testbed.protocol == Testbed.protocol_ssh:
        output = shell.execute_command(command=command,
                                        server=testbed.endpoint,
                                        params=params)
    else:
        return []

    return parse_func(output)

