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
# Module that constains the methods to be used by the rest of ALDE
#

import logging
import shell
from typing import List

import query
from models import db, Node, CPU, GPU, Testbed, Memory
import linux_probes.cpu_info_parser as parser
import slurm
import torque
from testbeds.constants import NAME
from testbeds.constants import MEMORY
from testbeds.constants import STATE
from testbeds.constants import GRES


# supported categories and corresponding module 
categories = {
    Testbed.slurm_category: slurm,
    Testbed.torque_category: torque,
}


def check_nodes_in_db_for_on_line_testbeds():
    """This function updates the list of nodes in the testbeds, 
    creating new discovered with respect to nodes in db, enabling nodes that
    were disabled but now and available, and disabling nodes that were available but now is
    not available. The full information of a node is not updated, just the list of nodes and
    the availability of each node"""
    for category in categories.keys():
        testbeds = query.get_online_testbeds(category)

        for testbed in testbeds:
            check_testbed_nodes_in_db(testbed)


def check_testbed_nodes_in_db(testbed: Testbed.Category):
    """This function is going to get all the nodes in the db that are online and
    of given category.

    For each node it is going to get the nodes and it is going to compare the
    information with the information in the db. It can happen two things:
        * If the node is in the db, info it is updated if necessary
        * If the node is not in the db, it is added

    After that, the method it is going to verify if there is a node that it is
    in the db but it is not in the list provided. If that happens, the node
    it is changed to disabled
    """
    module = categories.get(testbed.category, None)
    if module is None:
        logging.warning("Impossible to update testbed nodes for testbed " + testbed.name)
        return

    logging.info("Checking node info for testbed: " + testbed.name)

    nodes_from_manager = module.get_nodes_testbed(testbed)
    nodes_names_from_manager = [x[NAME] for x in nodes_from_manager]
    nodes_names_from_db = []
    nodes_ids = []
    for node in testbed.nodes:
        nodes_names_from_db.append(node.name)
        nodes_ids.append({'name' : node.name, 'id': node.id})

    nodes_in_manager_and_db = set(nodes_names_from_manager).intersection(set(nodes_names_from_db))
    nodes_in_manager_and_not_in_db = set(nodes_names_from_manager).difference(set(nodes_names_from_db))
    nodes_in_db_and_not_in_manager = set(nodes_names_from_db).difference(set(nodes_names_from_manager))

    # We add new nodes if not previously present in the db
    for node in nodes_in_manager_and_not_in_db:
        logging.info("Adding a new node: " + node + " to testbed: " + testbed.name)
        new_node = Node(name = node, information_retrieved = True)
        testbed.add_node(new_node)
        db.session.commit()

    # We check that the nodes in the db are updated if necessary
    for node in nodes_in_manager_and_db:
        interesting_nodes = [d for d in nodes_ids if d['name'] == node]

        for node_id in interesting_nodes:
            node_from_db = db.session.query(Node).filter_by(id=node_id['id']).first()
            if node_from_db.disabled:
                logging.info("Enabling node: " + node)
                node_from_db.disabled = False
                db.session.commit()

    # We check that the nodes not returned by slurm are set to 0
    for node in nodes_in_db_and_not_in_manager:
        interesting_nodes = [d for d in nodes_ids if d['name'] == node]

        for node_id in interesting_nodes:
            node_from_db = db.session.query(Node).filter_by(id=node_id['id']).first()

            if not node_from_db.disabled:
                logging.info("Disabling node: " + node)
                node_from_db.disabled = True
                db.session.commit()


def update_cpu_node_information():
    """Updates the CPU information for all nodes in all testbeds"""

    for category in categories.keys():
        testbeds = query.get_online_testbeds(category)

        for testbed in testbeds:
            update_testbed_cpu_node_information(testbed)


def update_testbed_cpu_node_information(testbed: Testbed):
    """This method updates the CPU information of nodes of a testbed.

    It is going to try to ssh into the node if the node is enabled. If an
    error occours it keeps the node information as is. If no error occours
    updates the entries in the db deleting the old CPU information first.
    """
    for node in testbed.nodes:
        if not node.disabled:
            cpus = parser.get_cpuinfo_node(testbed, node)

            if cpus != []:
                logging.info("Updating CPU info for node: " + node.name)
                db.session.query(CPU).filter_by(node_id=node.id).delete()
                node.cpus = cpus
                db.session.commit()
            else:
                logging.error("Impossible to update CPU info for node: " + node.name)


def update_node_information():
    """This function gets all the testbed that have been
    configured to retrieve all information automatically and
    update the node information if necessary
    """
    for category in categories.keys():
        testbeds = query.get_online_testbeds(category)

        for testbed in testbeds:
            update_testbed_node_information(testbed)


def update_testbed_node_information(testbed: Testbed):
    """Update the information from nodes in the given testbed according to the information
    retrieved from the workload manager"""
    module = categories.get(testbed.category, None)
    if module is None:
        logging.warning("Impossible to update testbed node information for testbed " + testbed.name)
        return
    nodes_info = module.get_node_information(testbed)

    for node_info in nodes_info:

        if NAME in node_info:
            node = db.session.query(Node).filter_by(
                        testbed_id=testbed.id,
                        name=node_info[NAME]).first()

            if node and STATE in node_info:
                logging.info("Updating information for node: " + node.name + " if necessary")
                node.state = node_info[STATE]
                db.session.commit()

            if node and MEMORY in node_info:
                logging.info("Updating memory information for node: " + node.name)
                db.session.query(Memory).filter_by(node_id=node.id).delete()
                memory = module.parse_memory(node_info[MEMORY])
                node.memories = [ memory ]
                db.session.commit()

            if node and GRES in node_info:
                resources = module.parse_gre_field_info(node_info[GRES])
                if 'gpu' in resources:
                    db.session.query(GPU).filter_by(node_id=node.id).delete()
                    logging.info("Updating gpu information for node: " + node.name)
                    node.gpus = resources['gpu']
                    db.session.commit()
