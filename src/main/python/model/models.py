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

class Memory(Base):
    """
    Object model of the RAM that can have a node in the Application
    Lifecycle Deployment Engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'memories'
    id = Column(Integer, primary_key=True)
    size = Column(Integer)
    units = Column(String)
    address = Column(String)
    memory_type = Column(String)

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


class CPU(Processor, Base):
    """This class represents the basic information of a CPU"""

    # SQLAlchemy mapping code
    __tablename__ = 'cpus'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(String)
    model_name = Column(String)
    arch = Column(String)
    model = Column(String)
    speed = Column(String)
    fpu = Column(Boolean)
    cores = Column(Integer)
    cache = Column(String)
    flags = Column(String)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="cpus")

    def __init__(self, vendor_id, model_name, arch, model, speed, fpu, cores, cache, flags):
        """Initialize the basic attributes of a CPU"""

        super().__init__(vendor_id, model_name)
        self.arch = arch
        self.model = model
        self.speed = speed
        self.fpu = fpu
        self.cores = cores
        self.cache = cache
        self.flags = flags

class GPU(Processor, Base):
    """This class represents the basic information of a GPU"""

    # SQLAlchemy mapping code
    __tablename__ = 'gpus'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(String)
    model_name = Column(String)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="gpus")

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
    cpus = relationship("CPU", order_by=CPU.id, back_populates="node")
    gpus = relationship("GPU", order_by=GPU.id, back_populates="node")

    def __init__(self, name, information_retrieved):
        """ Initialize the basis attributes for the testbed class """

        self.name = name
        self.information_retrieved = information_retrieved
        self.cpus = []
        self.gpus = []
        self.mcps = []
        self.memories = []
        self.status = {}

    def add_cpu(self, cpu):
        """ It adds a new cpu element to the node """

        if isinstance(cpu, CPU):
            self.cpus.append(cpu)

    def remove_cpu(self, cpu):
        """ It removes a CPU to the node """

        if cpu in self.cpus:
            self.cpus.remove(cpu)

    def add_gpu(self, gpu):
        """ It adds a new GPU element to the node """

        if isinstance(gpu, GPU):
            self.gpus.append(gpu)

    def remove_gpu(self, gpu):
        """ It removes a CPU to the node """

        if gpu in self.gpus:
            self.gpus.remove(gpu)

    def add_mcp(self, mcp):
        """ It adds a new MCP element to the node """

        if isinstance(mcp, MCP):
            self.mcps.append(mcp)

    def remove_mcp(self, mcp):
        """ It removes a MCP to the node """

        if mcp in self.mcps:
            self.mcps.remove(mcp)

    def add_memory(self, memory):
        """ It adds a new Memory element to the node """

        if isinstance(memory, Memory):
            self.memories.append(memory)

    def remove_memory(self, memory):
        """ It removes a Memory to the node """

        if memory in self.memories:
            self.memories.remove(memory)

    def add_status(self, key, value):
        """ All the elements in the status are dictionaries """

        if isinstance(key, str) and isinstance(value, dict):
            self.status[key] = value

    def remove_status(self, key):
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
