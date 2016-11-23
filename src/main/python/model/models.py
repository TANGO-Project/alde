# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from model.base import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Memory():
    """
    Object model of the RAM that can have a node in the Application
    Lifecycle Deployment Engine
    """

    def __init__(self, size, units, address='', memory_type=''):
        """Initialize the basis attributes for the tetbed class"""

        self.memory_type = memory_type
        self.address = address
        self.size = size
        self.units = units

class Processor():
    """This class represents the basic information for all types of processors.
       From CPU, FPGA, GPUs... etc..."""

    def __init__(self, vendor_id, model_name):
        """Initialize the basic attributes of the class"""

        self.vendor_id = vendor_id
        self.model_name = model_name


class CPU(Processor):
    """This class represents the basic information of a CPU"""

    def __init__(self, vendor_id, model_name, arch, model, cpu_speed, fpu, cpu_cores, cache, flags):
        """Initialize the basic attributes of a CPU"""

        super().__init__(vendor_id, model_name)
        self.arch = arch
        self.model = model
        self.cpu_speed = cpu_speed
        self.fpu = fpu
        self.cpu_cores = cpu_cores
        self.cache = cache
        self.flags = flags

class GPU(Processor):
    """This class represents the basic information of a GPU"""

    def __init__(self, vendor_id, model_name):
        """Initializes the basic attributes of a GPU"""

        super().__init__(vendor_id, model_name)
        self.memory = []

    def add_memory(self, memory):
        """It adds a new memory element to the GPU"""

        if isinstance(memory, Memory):
            self.memory.append(memory)

    def remove_memory(self, memory):
        """It removes a memory element of the GPU"""

        if memory in self.memory:
            self.memory.remove(memory)


class MCP(GPU):
    """ This class representes a Many Core Processor """

    def __init__(self, vendor_id, model_name):
        """Initializes the basic attributes of a MCP"""

        super().__init__(vendor_id, model_name)


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
    testbed_id = Column(Integer, ForeignKey('testbeds.id'))
    testbed = relationship("Testbed", back_populates="nodes")

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
    nodes = relationship("Node", order_by=Node.id, back_populates="testbed")

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
