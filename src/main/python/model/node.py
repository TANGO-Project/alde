# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from builtins import str
from model.base import Base
from model.memory import Memory
from model.processor import GPU, CPU, MCP
from sqlalchemy import Column, Integer, String, Boolean

class Node(Base):
    """
    Object model of the node connected to the Application Lifececyle
    Deployment engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    information_retrieved = Column(Boolean)

    def __init__(self, name, information_retrieved):
        """ Initialize the basis attributes for the testbed class """

        self.name = name
        self.information_retrieved = information_retrieved
        self.architecture = []
        self.status = {}

    def add_architecture_element(self, e):
        """ It adds a new architecture element to the node """

        if isinstance(e, Memory) or isinstance(e, GPU) or isinstance(e, CPU) or isinstance(e, MCP):
            self.architecture.append(e)

    def remove_architecture_element(self, element):
        """ It removes an architecture element to the node """

        if element in self.architecture:
            self.architecture.remove(element)

    def add_status_element(self, key, value):
        """ All the elements in the status are dictionaries """

        if isinstance(key, str) and isinstance(value, dict):
            self.status[key] = value

    def remove_status_element(self, key):
        """ Removes status element by key """

        if key in self.status.keys():
            del self.status[key]
