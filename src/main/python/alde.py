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
#  REST API for Application Lifecycle Deployment Engine 
#

import flask
import flask_restless
import slurm
import logging
import executor
from flask_apscheduler import APScheduler
from flask import current_app as current
from models import db, Application, ExecutionConfiguration, Testbed, Node, Memory, CPU, MCP, GPU, Deployment, Executable, Execution

url_prefix_v1='/api/v1'
accepted_message = { 'create' : True, 'reason' : ''}
testbed_not_configured_message = { 'create' : False,
                                   'reason' : 'Testbed is configured to automatically retrieve information of nodes'}
no_testbed = 'Testbed does not exist'
app_upload_folder = ''

class Config(object):
    """
    It defines the tasks jobs that need to be executed periodically...
    """

    JOBS = [
        {
            'id': 'check_nodes_in_db_for_on_line_testbeds',
            'func': 'slurm:check_nodes_in_db_for_on_line_testbeds',
            'args': (),
            'trigger': 'interval',
            'seconds': 60 
        },
        {
            'id': 'update_node_info',
            'func': 'slurm:update_node_information',
            'args': (),
            'trigger': 'interval',
            'seconds': 70 
        },
        {
            'id': 'update_cpu_node_info',
            'func': 'slurm:update_cpu_node_information',
            'args': (),
            'trigger': 'interval',
            'seconds': 80 
        },
        {
            'id': 'check_not_compiled_apps',
            'func': 'compilation.compiler:compile_executables',
            'args': (),
            'trigger': 'interval',
            'seconds': 31 
        },
        {
            'id': 'check_running_app_status',
            'func': 'executor:monitor_execution_apps',
            'args': (),
            'trigger': 'interval',
            'seconds': 20 
        },
    ]

    SCHEDULER_API_ENABLED = True

def _testbed_creation_node(testbed):
    """
    Internal function to check if the testbed exists and allow or not the
    creation of a node
    """

    if testbed == None :
        return { 'create' : False, 'reason' : no_testbed }
    elif testbed.on_line :
        return testbed_not_configured_message
    else:
        return accepted_message

def can_create_the_node(node=None, testbed_id=-1, testbed=None):
    """
    It checks if it is possible to add a Node.
    It is necessary to check first if the testbed exits in the db
    Or if the is due to the creation of the own testbed
    Or if the node is independent and not associated to a testbed.
    """

    if testbed_id == -1 and testbed == None :
        if node.testbed_id == None :
            return accepted_message
        else:
            testbed = db.session.query(Testbed).filter_by(id=node.testbed_id).first()
            return _testbed_creation_node(testbed)

    elif testbed_id != -1 :
        testbed = db.session.query(Testbed).filter_by(id=testbed_id).first()
        return _testbed_creation_node(testbed)

    else:
        if testbed['on_line'] :
            return testbed_not_configured_message
        else:
            return accepted_message

def put_testbed_preprocessor(instance_id=None, data=None, **kw):
    """
    It is going to check if the testbed allows the creation of nodes
    """

    if instance_id != None :

        if 'nodes' in data :
            create =  can_create_the_node(testbed_id=instance_id)

            if not create['create'] and create['reason'] != no_testbed :
                raise flask_restless.ProcessingException(
                                                description=create['reason'],
                                                code=405)

def put_node_preprocessor(instance_id=None, data=None, **kw):
    """
    It changes the state of a node
    """

    drain_reason = 'TANGO SAM requested to drain the node'

    if instance_id != None :

        if 'reason' in data:
            drain_reason = data['reason']

        if 'state' in data:
            if data['state'] == 'drain' :
                print(data)
                print('it arrives here...')
                executor.drain_a_node(instance_id, drain_reason)
            elif data['state'] == 'idle':
                executor.idle_a_node(instance_id)


def post_testbed_preprocessor(data=None, **kw):
    """
    It checks the data in the testbed payload to check if it is possible to
    add nodes to if necessaryexi
    """

    if 'nodes' in data :
        create = can_create_the_node(testbed=data)

        if not create['create'] :
            raise flask_restless.ProcessingException(
                                            description=create['reason'],
                                            code=405)

def patch_execution_script_preprocessor(instance_id=None, data=None, **kw):
    """
    It is going to start the execution of an application in the selected testbed
    """

    if 'launch_execution' in data :
        if data['launch_execution']:
            execution_script = db.session.query(ExecutionConfiguration).filter_by(id=instance_id).first()

            deployment = db.session.query(Deployment).filter_by(executable_id=execution_script.executable_id, testbed_id=execution_script.testbed_id).first()

            if not deployment:
                raise flask_restless.ProcessingException(
                                            description='No deployment configured to execute the application',
                                            code=409)

            elif not execution_script.testbed.on_line:
                raise flask_restless.ProcessingException(
                                            description='Testbed does not allow on-line connection',
                                            code=403)

            else:
                create_profile = False
                use_storaged_profile = False
                if 'create_profile' in data :
                    if data['create_profile']:
                        create_profile = True
                elif 'use_storaged_profile' in data :
                    if data['use_storaged_profile'] :
                        if execution_script.profile_file :
                            use_storaged_profile = True

                executor.execute_application(execution_script, create_profile, use_storaged_profile)

def patch_execution_preprocessor(instance_id=None, data=None, **kw):
    """
    It allows to change the status of a running execution
    """

    execution = db.session.query(Execution).filter_by(id=instance_id).first()

    if execution :

        if 'status' in data:
            if data['status'] == Execution.__status_cancel__ :
                url = execution.execution_configuration.testbed.endpoint
                executor.cancel_execution(execution, url) 
            elif data['status'] == Execution.__status_stop__ or  data['status'] == Execution.__status_restart__:
                if Application.CHECKPOINTABLE == execution.execution_configuration.application.application_type :
                    if ( execution.status == Execution.__status_running__ or execution.status == Execution.__status_restarted__ ) and data['status'] == Execution.__status_stop__  :
                        executor.stop_execution(execution)
                    elif execution.status == Execution.__status_stopped__ and data['status'] == Execution.__status_restart__ :
                        executor.restart_execution(execution)
                    else :
                        description = 'Execution is not in right state'
                        raise flask_restless.ProcessingException(description=description, code=409)
                else :
                    description = 'No a ' + Application.CHECKPOINTABLE + ' application type'
                    raise flask_restless.ProcessingException(description=description, code=409)
            else :
                raise flask_restless.ProcessingException(
                                description='No valid state to try to change',
                                code=409)
        elif 'add_resource' in data:
            executor.add_resource(execution)
        elif 'remove_resource' in data:
            executor.remove_resource(execution)
        else :
           raise flask_restless.ProcessingException(
                                description='No status, remove_resource, or add_resource field in the payload',
                                code=409)      
    else :
        raise flask_restless.ProcessingException(
                                description='No execution by the given id',
                                code=409)


def post_deployment_preprocessor(data=None, **kw):
    """
    It verifies that an executable can be uploaded to the testbed
    """

    # We verify the id is in the right format
    if 'testbed_id' in data :
        if 'executable_id' in data :

            # We verify that the testbed exists in the database
            testbed = db.session.query(Testbed).filter_by(id=data['testbed_id']).first()

            if testbed :
                # We verify now that the executable_id is present in the db
                executable = db.session.query(Executable).filter_by(id=data['executable_id']).first()

                if executable :
                    # We verify that the testbed is on-line
                    if testbed.on_line :
                        pass
                    else :
                        raise flask_restless.ProcessingException(
                        description='Testbed is off-line, this process needs to be performed manually',
                        code=403)
                else :
                    raise flask_restless.ProcessingException(
                        description='No executable found with that id in the database',
                        code=400)
            else :
                raise flask_restless.ProcessingException(
                description='No testbed found with that id in the database',
                code=400)
        else :
            raise flask_restless.ProcessingException(
                description='Missing executable_id field in the inputed JSON',
                code=400)
    else :
        raise flask_restless.ProcessingException(
                description='Missing testbed_id field in the inputed JSON',
                code=400)

def post_deployment_postprocessor(result=None):
    """
    It starsts the uploading process of a deployment to the testbed
    """

    executable = db.session.query(Executable).filter_by(id=result['executable_id']).first()
    testbed = db.session.query(Testbed).filter_by(id=result['testbed_id']).first()

    executor.upload_deployment(executable, testbed)

def post_and_patch_application_preprocessor(data=None, **kw):
    """
    It is going to start the execution of an application in the selected testbed
    """
    
    app_types = current.config['APP_TYPES']

    if 'application_type' in data :
        if data['application_type'] in app_types :
            pass
        else :
            raise flask_restless.ProcessingException(
                description='Application type ' + data['application_type'] + ' not supported',
                code=406
            )


def create_app_v1(sql_db_url, 
                  port, 
                  app_folder, 
                  profile_folder, 
                  app_types,
                  comparator_path,
                  comparator_file):
    """
    It creates the Flask REST app service
    """

    # We create the Flask Apo
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = sql_db_url
    app.config['LIVESERVER_PORT'] = port
    app.config['UPLOAD_FOLDER'] = app_folder
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app.config['APP_FOLDER'] = app_folder
    app.config['APP_PROFILE_FOLDER'] = profile_folder
    app.config['APP_TYPES'] = app_types
    app.config['COMPARATOR_PATH'] = comparator_path
    app.config['COMPARATOR_FILE'] = comparator_file
    app.config.from_object(Config())
    db.init_app(app)
    db.app=app

    # Create the Flask-Restless API manager.
    manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

    # Create the REST methods for an Application
    manager.create_api(Application,
                       methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
                       preprocessors={
                           'POST': [post_and_patch_application_preprocessor],
                           'PATCH_SINGLE': [post_and_patch_application_preprocessor]
                       },
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST API for the Executable Configuration
    manager.create_api(Executable,
                       methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST API for the Executable Configuration
    manager.create_api(Execution,
                       methods=['GET', 'PATCH'],
                       preprocessors={
                            'PATCH_SINGLE': [patch_execution_preprocessor]
                        },
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST API for Execution Configuration
    manager.create_api(ExecutionConfiguration,
                      methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
                      preprocessors={
                            'PATCH_SINGLE': [patch_execution_script_preprocessor]
                        },
                      url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST APi for the deployment
    manager.create_api(Deployment,
                       methods=['GET', 'POST'],
                       preprocessors={
                            'POST': [post_deployment_preprocessor]
                            },
                       postprocessors={
                            'POST': [post_deployment_postprocessor]
                       },
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST methods for a Testbed
    manager.create_api(Testbed,
                       methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
                       preprocessors={
                            'POST': [post_testbed_preprocessor],
                            'PATCH_SINGLE': [put_testbed_preprocessor],
                            'PUT_SINGLE': [put_testbed_preprocessor]
                            },
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create teh REST methods for a Node
    manager.create_api(Node,
                       methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                       preprocessors={
                           'PATCH_SINGLE': [put_node_preprocessor]
                       },
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST methods for the GPU
    manager.create_api(GPU,
                       methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST methods for the MCP
    manager.create_api(MCP,
                       methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST methods for the Memory
    manager.create_api(Memory,
                       methods=['GET', 'POST', 'PUT', 'DELETE'],
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the REST methods for the CPU
    manager.create_api(CPU,
                       methods=['GET', 'POST', 'PUT', 'DELETE'],
                       url_prefix=url_prefix_v1, results_per_page=-1)

    # Create the scheduler of tasks
    scheduler = APScheduler()
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()

    return app


