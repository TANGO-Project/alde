# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExecutionScript(db.Model):
    """
    Object that represetns all the information for executing an
    application into a testbed by the ALDE
    """

    # SQLAlchemy mapping code
    __tablename__ = 'execution_scripts'
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String)
    execution_type = db.Column(db.String)
    parameters = db.Column(db.String)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    application = db.relationship("Application", back_populates=("execution_scripts"))
    #testbed_id = db.Column(db.Integer, db.ForeignKey('testbeds.id'))
    #testbed = db.relationship("Testbed")

    def __init__(self, command, execution_type, parameters):
        """Initialize basic parameters of the class"""

        self.command = command
        self.execution_type = execution_type
        self.parameters = parameters

class Application(db.Model):
    """
    Object that represents all the information for an
    application that it needs to be build and maybe deploy by the
    Application Lifecycle Deployment Engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    execution_scripts = db.relationship("ExecutionScript", order_by=ExecutionScript.id, back_populates="application")


    def __init__(self, name):
        """Initializes the basic parameters of the class"""

        self.name = name

class Memory(db.Model):
    """
    Object model of the RAM that can have a node in the Application
    Lifecycle Deployment Engine
    """

    KILOBYTE = "kilobyte"
    MEGABYTE = "megabyte"
    GIGABYTE = "gigabyte"

    # SQLAlchemy mapping code
    __tablename__ = 'memories'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.Integer)
    units = db.Column(db.String)
    address = db.Column(db.String)
    memory_type = db.Column(db.String)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    node = db.relationship("Node", back_populates="memories")

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


class CPU(Processor, db.Model):
    """This class represents the basic information of a CPU"""

    # SQLAlchemy mapping code
    __tablename__ = 'cpus'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String)
    model_name = db.Column(db.String)
    arch = db.Column(db.String)
    model = db.Column(db.String)
    speed = db.Column(db.String)
    fpu = db.Column(db.Boolean)
    fpu_exception = db.Column(db.Boolean)
    cores = db.Column(db.Integer)
    core_id = db.Column(db.Integer)
    siblings = db.Column(db.Integer)
    stepping = db.Column(db.Integer)
    microcode = db.Column(db.String)
    physical_id = db.Column(db.Integer)
    wp = db.Column(db.Boolean)
    bogomips = db.Column(db.String)
    cache = db.Column(db.String)
    flags = db.Column(db.String)
    threads_per_core = db.Column(db.Integer)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    node = db.relationship("Node", back_populates="cpus")

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

class GPU(Processor, db.Model):
    """This class represents the basic information of a GPU"""

    # SQLAlchemy mapping code
    __tablename__ = 'gpus'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String)
    model_name = db.Column(db.String)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    node = db.relationship("Node", back_populates="gpus")

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


class Node(db.Model):
    """
    Object model of the node connected to the Application Lifececyle
    Deployment engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    information_retrieved = db.Column(db.Boolean)
    disabled = db.Column(db.Boolean)
    state = db.Column(db.String)
    testbed_id = db.Column(db.Integer, db.ForeignKey('testbeds.id'))
    testbed = db.relationship("Testbed", back_populates="nodes")
    cpus = db.relationship("CPU", order_by=CPU.id, back_populates="node")
    gpus = db.relationship("GPU", order_by=GPU.id, back_populates="node")
    memories = db.relationship("Memory", order_by=Memory.id, back_populates="node")

    def __init__(self, name, information_retrieved):
        """ Initialize the basis attributes for the testbed class """

        self.name = name
        self.disabled = False
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


class Testbed(db.Model):
    """
    Object model of the testbed connected to the Application Lifececyle
    Deployment engine
    """

    # Categories of testbeds
    slurm_category = 'SLURM'
    protocol_local = 'LOCAL'
    protocol_ssh = 'SSH'

    # SQLAlchemy mapping code
    __tablename__ = 'testbeds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    on_line = db.Column(db.Boolean)
    category = db.Column(db.String)
    protocol = db.Column(db.String)
    endpoint = db.Column(db.String)
    #package_formats = db.Column(db.String)
    nodes = db.relationship("Node", order_by=Node.id, back_populates="testbed")

    def __init__(self, name, on_line, category, protocol, endpoint, package_formats=[]):
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
