# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from model.base import Base
from model.node import Node
from sqlalchemy import Column, Integer, String, Boolean

class Testbed(Base):
    """
    Object model of the testbed connected to the Application Lifececyle
    Deployment engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'testbeds'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    on_line = Column(Boolean)
    protocol = Column(String)
    endpoint = Column(String)
    #package_formats = Column(String)

    def __init__(self, name, on_line, category, protocol, endpoint, package_formats):
        """Initialize the basis attributes for the testbed class"""

        self.name = name
        self.on_line = on_line
        self.category = category
        self.protocol = protocol
        self.endpoint = endpoint
        self.package_formats = package_formats
        self.nodes = []

    def add_node(self, node):
        """Adds a node to the list of nodes available in the testbed"""

        if isinstance(node, Node):
            self.nodes.append(node)

    def remove_node(self, node):
        """Removes a node of the list of nedes in the testbed"""

        if node in self.nodes:
            self.nodes.remove(node)
