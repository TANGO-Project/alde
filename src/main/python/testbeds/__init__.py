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
# Module that contains the code that handles the workload managers
#
# Supported workload managers must be configured in the facade.categories dictionary.
#
# Each module implementing the support of a workload manager must contain the following functions:
# * get_nodes_testbed: get the list of nodes
# * get_node_information: get detailed information of the nodes
# * parse_memory: get the Memory entity for a node from the string description
# * parse_gre_field_info: get the GPU entities for a node from the string description
#
# get_nodes_testbed and get_nodes_information can use the functions in testbeds.common
# to simplify the implementation, as the logic is the same and what is different is the 
# command to be executed and the parsing of the command output.
