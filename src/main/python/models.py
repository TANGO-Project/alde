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
# Object models definition being used by the Application Lifecycle Manager
#

from flask_sqlalchemy import SQLAlchemy
import simplejson
import sqlalchemy as sqla
from sqlalchemy.ext.mutable import MutableDict

# TODO update whole code with the possibility of recompiling the code, that will need to be automatically redeployed.

db = SQLAlchemy()

# This table makes the many to many relation between execution and nodes
execution_nodes_association_table = db.Table('executions_nodes', db.metadata,
    db.Column('execution_id', db.Integer, db.ForeignKey('executions.id')),
    db.Column('node_id', db.Integer, db.ForeignKey('nodes.id'))
)

class Deployment(db.Model):
    """
    This class represents the code being uploaded to a testbed
    to be executed and the status of it
    """

    __status_uploaded_updated__ = 'UPLOADED_UPDATED'
    __status_uploaded_not_updated__ = 'UPLOADED_NOT_UPDATED'
    __status_deleted__ = 'DELETED'

    # SQLAlchemy mapping code
    __tablename__ = 'deployments'
    executable_id = db.Column(db.Integer, 
                              db.ForeignKey('testbeds.id'), 
                              primary_key=True)
    testbed_id = db.Column(db.Integer, 
                           db.ForeignKey('executables.id'), 
                           primary_key=True)
    status = db.Column(db.String)
    path = db.Column(db.String)

class Executable(db.Model):
    """
    This entity represents the executable of an Application, it should include the source
    code from where the application was compiled together with the compilation script

    Execution script will be set later on when the testbed where the execution is going
    to happen is defined.
    """

    __status_not_compiled__ = 'NOT_COMPILED'
    __status_compiling__ = 'COMPILING'
    __status_compiled__ = 'COMPILED'
    __status_error_type__ = 'ERROR: UNKNOWN TYPE'
    __type_singularity_pm__ = 'SINGULARITY:PM'
    __type_singularity_srun__ = 'SINGULARITY:SRUN'
    __type_slurm_srun__ = 'SLURM:SRUN'
    __type_slurm_sbatch__ = 'SLURM:SBATCH'


    # SQLAlchemy mapping code
    __tablename__ = 'executables'
    id = db.Column(db.Integer, primary_key=True)
    source_code_file = db.Column(db.String)
    executable_file = db.Column(db.String)
    compilation_script = db.Column(db.String)
    compilation_type = db.Column(db.String)
    singularity_app_folder = db.Column(db.String)
    singularity_image_file = db.Column(db.String)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    application = db.relationship("Application", back_populates=("executables"))
    status = db.Column(db.String, default=__status_not_compiled__)

class Execution(db.Model):
    """
    Objet that represents the execution of an application with its
    different states

    ALTER TABLE executions ADD COLUMN extra_slurm_job_id VARCHAR;
    """
    __status_running__ = "RUNNING"
    __status_finished__ = "COMPLETED"
    __status_failed__ = "FAILED"
    __status_unknown__ = "UNKNOWN"
    __status_cancel__ = 'CANCEL'
    __status_cancelled__ = 'CANCELLED'

    # SQLAlchemy mapping code
    __tablename__ = 'executions'
    id = db.Column(db.Integer, primary_key=True)
    execution_type = db.Column(db.String)
    status = db.Column(db.String)
    output = db.Column(db.String)
    execution_configuration_id = db.Column(db.Integer, db.ForeignKey('execution_configurations.id'))
    execution_configuration = db.relationship("ExecutionConfiguration")
    slurm_sbatch_id = db.Column(db.Integer)
    nodes = db.relationship("Node", secondary=execution_nodes_association_table)
    parent_id = db.Column(db.Integer, db.ForeignKey('executions.id'))
    children = db.relationship("Execution",
                backref=db.backref('parent', remote_side=[id])
            )
    energy_output = db.Column(db.Integer)
    runtime_output = db.Column(db.Integer)
    add_resource = False

    def get_number_extra_jobs(self):
        """
        It returns the totaln number of
        extra jobs ids stored in extra_slurm_job_id
        """

        counter = 0
        for child in self.children:
            if child.status == Execution.__status_running__ :
                counter += 1

        return counter


class ExecutionConfiguration(db.Model):
    """
    Object that represetns all the information for executing an
    application into a testbed by the ALDE
    """

    # SQLAlchemy mapping code
    __tablename__ = 'execution_configurations'
    id = db.Column(db.Integer, primary_key=True)
    execution_type = db.Column(db.String)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    application = db.relationship("Application", back_populates=("execution_configurations"))
    testbed_id = db.Column(db.Integer, db.ForeignKey('testbeds.id'))
    testbed = db.relationship("Testbed")
    executable_id = db.Column(db.Integer, db.ForeignKey('executables.id'))
    executable = db.relationship("Executable")
    num_nodes = db.Column(db.Integer)
    num_gpus_per_node = db.Column(db.Integer)
    num_cpus_per_node = db.Column(db.Integer)
    exec_time = db.Column(db.Integer)
    command = db.Column(db.String)
    compss_config = db.Column(db.String)
    srun_config = db.Column(db.String)
    profile_file = db.Column(db.String)
    executions = db.relationship("Execution", order_by=Execution.id, back_populates="execution_configuration")
    launch_execution=False
    create_profile=False
    use_storaged_profile=False


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
    application_type = db.Column(db.String)
    max_power = db.Column(db.Float)
    max_power_units = db.Column(db.String)
    max_energy = db.Column(db.Float)
    max_energy_units = db.Column(db.String)
    priority = db.Column(db.Integer)
    deadline = db.Column(db.Integer)
    scaling_upper_bound = db.Column(db.Integer)
    scaling_lower_bound = db.Column(db.Integer)
    execution_configurations = db.relationship("ExecutionConfiguration", order_by=ExecutionConfiguration.id, back_populates="application")
    executables = db.relationship("Executable", order_by=Executable.id, back_populates="application")

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
    node = db.relationship("Node", back_populates="mcps")

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
    mcps = db.relationship("MCP", order_by=MCP.id, back_populates="node")
    memories = db.relationship("Memory", order_by=Memory.id, back_populates="node")
    status = {}
    reason = ''

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

class JsonEncodedDict(sqla.TypeDecorator):
  """Enables JSON storage by encoding and decoding on the fly."""
  impl = sqla.String

  def process_bind_param(self, value, dialect):
    return simplejson.dumps(value)

  def process_result_value(self, value, dialect):
    return simplejson.loads(value)

json_type = MutableDict.as_mutable(JsonEncodedDict)


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
    extra_config = db.Column(json_type)
    package_formats = db.Column(db.PickleType)
    nodes = db.relationship("Node", order_by=Node.id, back_populates="testbed")

    def __init__(self, name, on_line, category, protocol, endpoint, package_formats=[], extra_config=None):
        """Initialize the basis attributes for the testbed class"""

        self.name = name
        self.on_line = on_line
        self.category = category
        self.protocol = protocol
        self.endpoint = endpoint
        self.package_formats = package_formats
        self.nodes = []
        self.extra_config = extra_config

    def add_node(self, node):
        """Adds a node to the list of nodes available in the testbed"""

        if isinstance(node, Node):
            self.nodes.append(node)

    def remove_node(self, node):
        """Removes a node of the list of nedes in the testbed"""

        if node in self.nodes:
            self.nodes.remove(node)
