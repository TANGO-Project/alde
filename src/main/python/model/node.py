# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from model.memory import Memory

class Node():
    """Object model of the node connected to the Application Lifececyle
       Deployment engine"""

    def __init__(self, id, name, information_retrieved):
        """Initialize the basis attributes for the testbed class"""
        self.id = id
        self.name = name
        self.information_retrieved = information_retrieved
        self.architecture = []

    def add_architecture_element(self, element):
        """It adds a new architecture element to the node"""

        if isinstance(element, Memory):
            self.architecture.append(element)

    def remove_architecture_element(self, element):
        """It removes an architecture element to the node"""

        print("TODO")
