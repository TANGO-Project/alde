# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from flask import Flask
from flask_testing import TestCase
from models import db, ExecutionConfiguration, Application, Testbed, Node, Executable, Deployment, Execution
from unittest.mock import call
import alde
import json
import unittest.mock as mock
import executor

class AldeV1Tests(TestCase):
    """
    Test that verifies the REST API of Alde for its v1 version
    """

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    APP_FOLDER = "/tmp/app_folder"
    APP_TYPES = ['RIGID', 'MOULDABLE', 'CHECKPOINTABLE', 'MALLEABLE']

    def create_app(self):
        """
        It initializes the application
        """

        app = alde.create_app_v1(self.SQLALCHEMY_DATABASE_URI, 5101, self.APP_FOLDER, self.APP_FOLDER, self.APP_TYPES)

        return app

    def setUp(self):
        """
        It creates the memory db
        """

        db.create_all()

        # We store some Applications in the db for the tests
        application_1 = Application()
        application_1.name = 'AppName_1'
        application_2 = Application()
        application_2.name = 'AppName_2'

        # Adding executing scripts
        execution_script_1 = ExecutionConfiguration()
        execution_script_1.execution_type = "slurm:sbatch"
        execution_script_2 = ExecutionConfiguration()
        execution_script_2.execution_type = "slurm:sbatch2"
        application_2.execution_configurations = [
                execution_script_1,
                execution_script_2 ]


        db.session.add(application_1)
        db.session.add(application_2)

        # We store some testbeds in the db for the tests
        testbed_1 = Testbed("name_1", True, "slurm", "ssh", "user@server", ['slurm'])
        testbed_2 = Testbed("name_2", False, "slurm", "ssh", "user@server", ['slurm'])
        testbed_3 = Testbed("name_3", True, "slurm", "ssh", "user@server", ['slurm', 'slurm:singularity'])
        db.session.add(testbed_1)
        db.session.add(testbed_2)
        db.session.add(testbed_3)
        db.session.commit()

        deployment = Deployment()
        deployment.executable_id = execution_script_1.id
        deployment.testbed_id = testbed_1.id
        db.session.add(deployment)

        # We store some nodes in the db for the tests
        node_1 = Node("node_1", True)
        node_2 = Node("node_2", False)
        db.session.add(node_1)
        db.session.add(node_2)

        execution = Execution()
        execution.execution_type = "execution_type"
        execution.status = "status"
        db.session.add(execution)


        db.session.commit()

    def setDown(self):
        """
        Deletes everything in the memory db
        """

        db.session_remove()

    def test_execution_rest_api(self):
        """
        It tests the rest api for the exeuction entity
        """

        # GET
        response = self.client.get("/api/v1/executions")

        # We verify the response of the GET
        self.assertEquals(200, response.status_code)
        executions = response.json['objects']
        self.assertEquals(1, len(executions))
        execution = executions[0]
        self.assertEquals("execution_type", execution['execution_type'])
        self.assertEquals("status", execution['status'])

    def test_application_rest_api(self):
        """
        It tests all supported REST methods for an Application works
        as expected.
        """

        # GET
        response = self.client.get("/api/v1/applications")

        # We verify the respongse to the GET
        self.assertEquals(200, response.status_code)
        applications = response.json['objects']
        self.assertEquals(2, len(applications))
        application = applications[0]
        self.assertEquals(1, application['id'])
        self.assertEquals('AppName_1', application['name'])
        application = applications[1]
        self.assertEquals(2, application['id'])
        self.assertEquals('AppName_2', application['name'])

        # POST
        data={
                'name' : 'AppName_3'
            }

        response = self.client.post('/api/v1/applications',
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        self.assertEquals('AppName_3', response.json['name'])
        self.assertEquals(3, response.json['id'])
        # We check that we only have three applicions
        response = self.client.get("/api/v1/applications")
        self.assertEquals(3, len(response.json['objects']))

        # GET Specific Entity
        response = self.client.get("/api/v1/applications/1")

        self.assertEquals(200, response.status_code)
        self.assertEquals('AppName_1', response.json['name'])
        self.assertEquals(1, response.json['id'])

        # DELETE
        response = self.client.delete("/api/v1/applications/1")

        self.assertEquals(204, response.status_code)
        # We check that we only have two applicions
        response = self.client.get("/api/v1/applications")
        self.assertEquals(2, len(response.json['objects']))

    def test_executable_rest_api(self):
        """
        It tests all supported REST methods for an Executables works
        as expected.
        """
        
        # POST
        data={
            "executables" : [
                {
                    "compilation_script" : "compss_build_app Matmul",
                    "compilation_type" : "SINGULARITY:PM",
                    "source_code_file" : "dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip",
                    "singularity_image_file" : "asdfasd.img",
                    "singularity_app_folder" : "/tmp",
                    "status" : "COMPILED"
                }
            ]
        }


        response = self.client.put('/api/v1/applications/2',
                                      data=json.dumps(data),
                                      content_type='application/json')

        self.assertEquals(200, response.status_code)
        self.assertEquals(2, response.json['executables'][0]['application_id'])
        self.assertEquals('compss_build_app Matmul', response.json['executables'][0]['compilation_script'])
        self.assertEquals('SINGULARITY:PM', response.json['executables'][0]['compilation_type'])
        self.assertEquals(None, response.json['executables'][0]['executable_file'])
        self.assertEquals(1, response.json['executables'][0]['id'])
        self.assertEquals('/tmp', response.json['executables'][0]['singularity_app_folder'])
        self.assertEquals('asdfasd.img', response.json['executables'][0]['singularity_image_file'])
        self.assertEquals('dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip', response.json['executables'][0]['source_code_file'])
        self.assertEquals('COMPILED', response.json['executables'][0]['status'])

        # We check that we only have three applicions
        response = self.client.get("/api/v1/executables")
        self.assertEquals(1, len(response.json['objects']))

        # GET Specific Entity
        response = self.client.get("/api/v1/executables/1")

        self.assertEquals(200, response.status_code)
        self.assertEquals(2, response.json['application_id'])
        self.assertEquals('compss_build_app Matmul', response.json['compilation_script'])
        self.assertEquals('SINGULARITY:PM', response.json['compilation_type'])
        self.assertEquals(None, response.json['executable_file'])
        self.assertEquals(1, response.json['id'])
        self.assertEquals('/tmp', response.json['singularity_app_folder'])
        self.assertEquals('asdfasd.img', response.json['singularity_image_file'])
        self.assertEquals('dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip', response.json['source_code_file'])
        self.assertEquals('COMPILED', response.json['status'])
        
        # DELETE
        response = self.client.delete("/api/v1/executables/1")

        self.assertEquals(204, response.status_code)
        # We check that we only have two applicions
        response = self.client.get("/api/v1/executables")
        self.assertEquals(0, len(response.json['objects']))

        # POST
        data = {
                    "application_id" : 1,
                    "compilation_script" : "compss_build_app Matmul",
                    "compilation_type" : "SINGULARITY:PM",
                    "source_code_file" : "dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip",
                    "singularity_image_file" : "asdfasd.img",
                    "singularity_app_folder" : "/tmp",
                    "status" : "COMPILED"
                }

        # We check that we only have three applicions
        response = self.client.post("/api/v1/executables", 
                                    data=json.dumps(data),
                                    content_type='application/json')
        self.assertEquals(201, response.status_code)
        id = response.json['application_id']

        # GET Specific Entity
        response = self.client.get("/api/v1/executables/" + str(id))

        self.assertEquals(200, response.status_code)
        self.assertEquals(1, response.json['application_id'])
        self.assertEquals('compss_build_app Matmul', response.json['compilation_script'])
        self.assertEquals('SINGULARITY:PM', response.json['compilation_type'])
        self.assertEquals(None, response.json['executable_file'])
        self.assertEquals(id, response.json['id'])
        self.assertEquals('/tmp', response.json['singularity_app_folder'])
        self.assertEquals('asdfasd.img', response.json['singularity_image_file'])
        self.assertEquals('dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip', response.json['source_code_file'])
        self.assertEquals('COMPILED', response.json['status'])

        # PUT/PATCH
        data = {
                    "status" : "COMPILED2"
                }

        # We check that we only have three applicions
        response = self.client.put("/api/v1/executables/" + str(id),
                                    data=json.dumps(data),
                                    content_type='application/json')

        # GET Specific Entity
        response = self.client.get("/api/v1/executables/" + str(id))

        self.assertEquals(200, response.status_code)
        self.assertEquals(1, response.json['application_id'])
        self.assertEquals('compss_build_app Matmul', response.json['compilation_script'])
        self.assertEquals('SINGULARITY:PM', response.json['compilation_type'])
        self.assertEquals(None, response.json['executable_file'])
        self.assertEquals(id, response.json['id'])
        self.assertEquals('/tmp', response.json['singularity_app_folder'])
        self.assertEquals('asdfasd.img', response.json['singularity_image_file'])
        self.assertEquals('dc93830d-740e-40b4-80ed-777e1c6ee0ec.zip', response.json['source_code_file'])
        self.assertEquals('COMPILED2', response.json['status'])

    def test_testbed_rest_api(self):
        """
        It tests all supported REST methods for an Testbed works
        as expected.
        """

        # GET
        response = self.client.get("/api/v1/testbeds")

        # We verify the respongse to the GET
        self.assertEquals(200, response.status_code)
        testbeds = response.json['objects']
        testbed = testbeds[0]
        self.assertEquals("name_1", testbed['name'])
        self.assertTrue(testbed['on_line'])
        self.assertEquals("slurm", testbed['category'])
        self.assertEquals("ssh", testbed['protocol'])
        self.assertEquals("user@server", testbed['endpoint'])
        testbed = testbeds[1]
        self.assertEquals("name_2", testbed['name'])
        self.assertFalse(testbed['on_line'])
        self.assertEquals("slurm", testbed['category'])
        self.assertEquals("ssh", testbed['protocol'])
        self.assertEquals("user@server", testbed['endpoint'])

        # POST
        data={
                'name' : 'name_3',
                'on_line' : False,
                'category' : 'embedded',
                'protocol' : 'none',
                'endpoint' : 'compiled_to_disk',
                'extra_config' : {
                    'extra1_config' : 'config1',
                    'extra2_config' : 'config2'
                }
            }

        response = self.client.post("/api/v1/testbeds",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        testbed = response.json
        print(testbed)
        self.assertEquals("name_3", testbed['name'])
        self.assertFalse(testbed['on_line'])
        self.assertEquals("embedded", testbed['category'])
        self.assertEquals("none", testbed['protocol'])
        self.assertEquals("compiled_to_disk", testbed['endpoint'])
        self.assertEquals("config1", testbed['extra_config']['extra1_config'])
        self.assertEquals("config2", testbed['extra_config']['extra2_config'])
        # We check that we only have three testbeds
        response = self.client.get("/api/v1/testbeds")
        self.assertEquals(4, len(response.json['objects']))

        # GET Specific identity
        response = self.client.get("/api/v1/testbeds/4")
        self.assertEquals(200, response.status_code)
        testbed = response.json
        self.assertEquals("name_3", testbed['name'])
        self.assertFalse(testbed['on_line'])
        self.assertEquals("embedded", testbed['category'])
        self.assertEquals("none", testbed['protocol'])
        self.assertEquals("compiled_to_disk", testbed['endpoint'])

        # DELETE
        response = self.client.delete("/api/v1/testbeds/1")

        self.assertEquals(204, response.status_code)
        # We check we only have two entities in the db
        response = self.client.get("/api/v1/testbeds")
        self.assertEquals(3, len(response.json['objects']))

        # PUT
        data={"name": "Foobar"}

        response = self.client.put("api/v1/testbeds/2",
                                   data=json.dumps(data),
                                   content_type='application/json')

        self.assertEquals(200, response.status_code)
        testbed = response.json
        self.assertEquals("Foobar", testbed['name'])
        self.assertFalse(testbed['on_line'])
        self.assertEquals("slurm", testbed['category'])
        self.assertEquals("ssh", testbed['protocol'])
        self.assertEquals("user@server", testbed['endpoint'])

    def test_execution_script_rest_api(self):
        """
        It tests all supported REST methods for an ExeuctionScript works
        as expected.
        """

        # GET
        response = self.client.get("/api/v1/execution_configurations")

        # We verify the respongse to the GET
        self.assertEquals(200, response.status_code)
        execution_configurations = response.json['objects']
        execution_script = execution_configurations[0]
        self.assertEquals("slurm:sbatch", execution_script['execution_type'])
        execution_script = execution_configurations[1]
        self.assertEquals("slurm:sbatch2", execution_script['execution_type'])

        # POST
        data={
                'execution_type': 'slurm:sbatch3'
            }

        response = self.client.post("/api/v1/execution_configurations",
                                      data=json.dumps(data),
                                      content_type='application/json')

        self.assertEquals(201, response.status_code)
        execution_script = response.json
        self.assertEquals("slurm:sbatch3", execution_script['execution_type'])
        
        # We check that we only have three execution_configurations
        response = self.client.get("/api/v1/execution_configurations")
        self.assertEquals(3, len(response.json['objects']))

        # GET Specific identity
        response = self.client.get("/api/v1/execution_configurations/3")
        self.assertEquals(200, response.status_code)
        execution_script = response.json
        self.assertEquals("slurm:sbatch3", execution_script['execution_type'])

        # DELETE
        response = self.client.delete("/api/v1/execution_configurations/3")

        self.assertEquals(204, response.status_code)
        # We check we only have two entities in the db
        response = self.client.get("/api/v1/execution_configurations")
        self.assertEquals(2, len(response.json['objects']))

        # PUT
        data={"execution_type": "Foobar"}

        response = self.client.put("api/v1/execution_configurations/2",
                                    data=json.dumps(data),
                                    content_type='application/json')

        self.assertEquals(200, response.status_code)
        execution_script = response.json
        self.assertEquals("Foobar", execution_script['execution_type'])
        response = self.client.get("/api/v1/execution_configurations/2")
        self.assertEquals(200, response.status_code)
        execution_script = response.json
        self.assertEquals("Foobar", execution_script['execution_type'])


    def test_node_rest_api(self):
        """
        It tests all supported REST methods for an Testbed works
        as expected.
        """

        # GET
        response = self.client.get("/api/v1/nodes")

        # We verify the respongse to the GET
        self.assertEquals(200, response.status_code)
        nodes = response.json['objects']
        node = nodes[0]
        self.assertEquals("node_1", node['name'])
        self.assertTrue(node['information_retrieved'])
        node = nodes[1]
        self.assertEquals("node_2", node['name'])
        self.assertFalse(node['information_retrieved'])

        # POST
        data={
             'name' : 'node_3',
             'information_retrieved' : False,
         }

        response = self.client.post("/api/v1/nodes",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        node = response.json
        self.assertEquals("node_3", node['name'])
        self.assertFalse(node['information_retrieved'])
        # We check that we only have three testbeds
        response = self.client.get("/api/v1/nodes")
        self.assertEquals(3, len(response.json['objects']))

        # GET Specific identity
        response = self.client.get("/api/v1/nodes/3")
        self.assertEquals(200, response.status_code)
        node = response.json
        self.assertEquals("node_3", node['name'])
        self.assertFalse(node['information_retrieved'])

        # DELETE
        response = self.client.delete("/api/v1/nodes/1")

        self.assertEquals(204, response.status_code)
        # We check we only have two entities in the db
        response = self.client.get("/api/v1/nodes")
        self.assertEquals(2, len(response.json['objects']))

        # PUT
        data={"name": "Foobar"}

        response = self.client.put("api/v1/nodes/2",
                                   data=json.dumps(data),
                                   content_type='application/json')

        self.assertEquals(200, response.status_code)
        node = response.json
        self.assertEquals("Foobar", node['name'])
        self.assertFalse(node['information_retrieved'])

    def test_can_create_the_node(self):
        """
        Checks the right behaviour that checks if it is possible to add
        a node
        """

        # Node not associated to any db
        node = Node("xxx", True)

        is_possible = alde.can_create_the_node(node)
        self.assertEquals(True, is_possible['create'])
        self.assertEquals('', is_possible['reason'])

        # Node has an ivalid testbed id
        node.testbed_id = 100000

        is_possible = alde.can_create_the_node(node)
        self.assertEquals(False, is_possible['create'])
        self.assertEquals('Testbed does not exist', is_possible['reason'])

        # Testbed exists but information is retrieved automatically
        node.testbed_id = 1

        is_possible = alde.can_create_the_node(node)
        self.assertEquals(False, is_possible['create'])
        self.assertEquals('Testbed is configured to automatically retrieve information of nodes',
                          is_possible['reason'])

        # Testeb exists but information is not retrieved automatically
        node.testbed_id = 2

        is_possible = alde.can_create_the_node(node)
        self.assertEquals(True, is_possible['create'])
        self.assertEquals('', is_possible['reason'])

        # Testbed info is passed by the url:
        node = Node("xxx", True)
        ## Testbed does not allow it
        is_possible = alde.can_create_the_node(node, testbed_id=1)
        self.assertEquals(False, is_possible['create'])
        self.assertEquals('Testbed is configured to automatically retrieve information of nodes',
                          is_possible['reason'])
        ## Testbed does allow it
        is_possible = alde.can_create_the_node(node, testbed_id=2)
        self.assertEquals(True, is_possible['create'])
        self.assertEquals('', is_possible['reason'])

        # Testbed and nodes are created at the same time
        testbed_1 = {
                        'name' : 'name_3',
                        'on_line' : True
                    }
        testbed_2 = {
                        'name' : 'name_3',
                        'on_line' : False
                    }
        ## Testbed does not allow it
        is_possible = alde.can_create_the_node(node, testbed=testbed_1)
        self.assertEquals(False, is_possible['create'])
        self.assertEquals('Testbed is configured to automatically retrieve information of nodes',
                          is_possible['reason'])
        ## Testbed does allow it
        is_possible = alde.can_create_the_node(node, testbed=testbed_2)
        self.assertEquals(True, is_possible['create'])
        self.assertEquals('', is_possible['reason'])

    def test_testbed_node_insertions(self):
        """
        Tests the behaviour to see if the node gets associated
        to a testbed and how
        """

        ################
        # POST TESTBED #
        ################

        # Testbed is not on-line, it should allow it
        data={
                'name' : 'name_3',
                'on_line' : False,
                'category' : 'embedded',
                'protocol' : 'none',
                'endpoint' : 'compiled_to_disk',
                'nodes' : [
                            {
                                'name' : 'node_3',
                                'information_retrieved' : False
                            }
                           ]
            }
        response = self.client.post("/api/v1/testbeds",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        testbed = response.json
        self.assertEquals("name_3", testbed['name'])
        self.assertFalse(testbed['on_line'])
        self.assertEquals("embedded", testbed['category'])
        self.assertEquals("none", testbed['protocol'])
        self.assertEquals("compiled_to_disk", testbed['endpoint'])
        node = testbed['nodes'][0]
        self.assertEquals(False, node['information_retrieved'])
        self.assertEquals('node_3', node['name'])
        self.assertEquals(3, node['id'])

        # Testbed is on-line, it shouldn't allow it
        data={
                'name' : 'name_3',
                'on_line' : True,
                'category' : 'embedded',
                'protocol' : 'none',
                'endpoint' : 'compiled_to_disk',
                'nodes' : [
                            {
                                'name' : 'node_3',
                                'information_retrieved' : False
                            }
                           ]
            }
        response = self.client.post("/api/v1/testbeds",
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEquals(405, response.status_code)
        self.assertEquals(
          'Testbed is configured to automatically retrieve information of nodes',
          response.json['message'])

        ###############
        # PUT TESTBED #
        ###############

        data={
             'nodes' : [
                        {
                            'name' : 'node_3',
                            'information_retrieved' : False
                        }
                       ]
         }

        # Testbed 2 is off-line, so it should allow to add a node
        response = self.client.put("/api/v1/testbeds/2",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(200, response.status_code)
        node = response.json['nodes'][0]
        self.assertEquals(False, node['information_retrieved'])
        self.assertEquals('node_3', node['name'])
        self.assertEquals(4, node['id'])

        # Testbed 1 is on-line, so it shouldn't allow to add a node to it
        response = self.client.put("/api/v1/testbeds/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(405, response.status_code)
        self.assertEquals(
          'Testbed is configured to automatically retrieve information of nodes',
          response.json['message'])

        # Testbed does not exists in db
        response = self.client.put("/api/v1/testbeds/1000",
                                    data=json.dumps(data),
                                    content_type='application/json')

        self.assertEquals(404, response.status_code)

        ################
        # PATCH a Node #
        ################
        data={
             'nodes' : {
                        'add': [{
                                    'name' : 'node_3',
                                    'information_retrieved' : False
                               }]
                       }
         }

        # Testbed 2 is off-line, so it should allow to add a node
        response = self.client.patch("/api/v1/testbeds/2",
                                      data=json.dumps(data),
                                      content_type='application/json')

        self.assertEquals(200, response.status_code)
        node = response.json['nodes'][0]
        self.assertEquals(False, node['information_retrieved'])
        self.assertEquals('node_3', node['name'])
        self.assertEquals(4, node['id'])

        # Testbed 1 is on-line, so it shouldn't allow to add a node to it
        response = self.client.patch("/api/v1/testbeds/1",
                                      data=json.dumps(data),
                                      content_type='application/json')

        self.assertEquals(405, response.status_code)
        self.assertEquals(
           'Testbed is configured to automatically retrieve information of nodes',
           response.json['message'])

        # Testbed does not exists in db
        response = self.client.patch("/api/v1/testbeds/1000",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(404, response.status_code)

    @mock.patch('executor.execute_application')
    def test_patch_execution_script_preprocessor(self, mock_execute_application):
        """
        Verifies the correct work of the function.
        """

        # First we verify that nothing happens if launch_execution = False
        data = {'launch_execution': False}

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(200, response.status_code)
        execution_script = response.json
        self.assertEquals("slurm:sbatch", execution_script['execution_type'])

        """
        If the execution_script has not assigned a testbed we give an error
        returning a 409 Conflict in the resource
        """
        data = {'launch_execution': True}

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(409, response.status_code)
        execution_script = response.json
        self.assertEquals(
          'No deployment configured to execute the application',
          response.json['message'])

        """
        Now we have an off-line testbed testbed to submit the execution
        """
        testbed = Testbed("name", False, "slurm", "ssh", "user@server", ['slurm'])
        db.session.add(testbed)

        executable = Executable()
        executable.source_code_file = 'source_code_file'
        executable.compilation_script = 'compilation_script'
        executable.compilation_type = 'compilation_type'
        db.session.add(executable)

        db.session.commit()

        execution_script = db.session.query(ExecutionConfiguration).filter_by(id=1).first()
        execution_script.testbed = testbed
        execution_script.executable = executable

        db.session.commit()

        deployment = Deployment()
        deployment.executable_id = executable.id
        deployment.testbed_id = testbed.id
        db.session.add(deployment)
        db.session.commit()

        data = {'launch_execution': True}

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(403, response.status_code)
        self.assertEquals(
          'Testbed does not allow on-line connection',
          response.json['message'])

        """
        Now we are able to launch the execution
        """
        testbed.on_line = True
        db.session.commit()

        data = {'launch_execution': True}

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                    content_type='application/json')

        self.assertEquals(200, response.status_code)

        """
        Now we are able to lauch the execution with create_profile= True
        """
        data = { 'launch_execution': True, 'create_profile': True }

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        """
        Now we are able to lauch the execution with use_storaged_profile=true and create_profile=True
        """
        data = { 'launch_execution': True, 
                 'create_profile': True,
                 'use_storaged_profile': True }

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        """
        Now we are able to lauch the execution with use_storaged_profile=true 
        and Execution_Configuration without any profile storaged on it.
        """
        data = { 'launch_execution': True, 
                  'use_storaged_profile': True }

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        """
        Now we are able to lauch the execution with use_storaged_profile=true 
        and Execution_Configuration with a profile storaged on it.
        """
        data = { 'launch_execution': True, 
                  'use_storaged_profile': True }

        execution_script = db.session.query(ExecutionConfiguration).filter_by(id=1).first()
        execution_script.profile_file = 'pepito.profile'
        db.session.commit()

        response = self.client.patch("/api/v1/execution_configurations/1",
                                     data=json.dumps(data),
                                     content_type='application/json')

        call_1 = call(execution_script, False, False)
        call_2 = call(execution_script, True, False)
        call_3 = call(execution_script, True, False)
        call_4 = call(execution_script, False, False)
        call_5 = call(execution_script, False, True)
        
        calls = [ call_1, call_2, call_3, call_4, call_5 ]
        mock_execute_application.assert_has_calls(calls)

    @mock.patch('executor.remove_resource')
    @mock.patch('executor.add_resource')
    @mock.patch('executor.cancel_execution')
    def test_patch_execution_preprocessor(self, mock_executor_cancel, mock_executor_add, mock_executor_remove):
        """
        It test the correct work of the method of canceling an execution
        """

        # First we verify that nothing happens if launch_execution = False
        data = {'status': 'PEPITO'}

        response = self.client.patch("/api/v1/executions/100",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(409, response.status_code)
        self.assertEquals(
          'No execution by the given id',
          response.json['message'])

        # Preparing the data for the rest of the test
        testbed = Testbed("name", False, "slurm", "ssh", "user@server", ['slurm'])
        db.session.add(testbed)
        db.session.commit()
        execution_configuration = ExecutionConfiguration()
        execution_configuration.testbed = testbed
        db.session.add(execution_configuration)
        db.session.commit()
        execution = Execution()
        execution.execution_type = Executable.__type_singularity_srun__
        execution.status = Execution.__status_running__
        execution.execution_configuration = execution_configuration
        db.session.add(execution)
        db.session.commit()

        response = self.client.patch("/api/v1/executions/" + str(execution.id) ,
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEquals(409, response.status_code)
        self.assertEquals(
          'No valid state to try to change',
          response.json['message'])

        data = {'PEPITO': 'PEPITO'}
        response = self.client.patch("/api/v1/executions/" + str(execution.id) ,
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(409, response.status_code)
        self.assertEquals(
          'No status, remove_resource, or add_resource field in the payload',
          response.json['message'])

        data = {'status': 'CANCEL'}
        response = self.client.patch("/api/v1/executions/" + str(execution.id) ,
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(200, response.status_code)
        mock_executor_cancel.assert_called_with(execution, 'user@server')

        data = {'add_resource': ''}
        response = self.client.patch("/api/v1/executions/" + str(execution.id) ,
                                     data=json.dumps(data),
                                     content_type='application/json')

        mock_executor_add.assert_called_with(execution)

        data = {'remove_resource': ''}
        response = self.client.patch("/api/v1/executions/" + str(execution.id) ,
                                     data=json.dumps(data),
                                     content_type='application/json')

        mock_executor_remove.assert_called_with(execution)

    @mock.patch('executor.upload_deployment')
    def test_post_deployment_preprocessor(self, mock_upload_deployment):
        """
        It checks the correct work of the post_deployment_preprocessor function
        """

        # Error raised becasue missing testbed_id
        data = { 'asdf' : 'asdf'}

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(400, response.status_code)
        self.assertEquals('Missing testbed_id field in the inputed JSON', response.json['message'])

        # Error raised because missing executable_di
        data = { 'asdf' : 'asdf',
                 'testbed_id' : 1 }

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(400, response.status_code)
        self.assertEquals('Missing executable_id field in the inputed JSON', response.json['message'])

        # Error raised because the testbed_id is wrong
        data = { 'executable_id' : 1,
                 'testbed_id' : 5 }

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(400, response.status_code)
        self.assertEquals('No testbed found with that id in the database', response.json['message'])

        # Error raised because the executable_id is wrong
        data = { 'executable_id' : 1,
                 'testbed_id' : 1 }

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(400, response.status_code)
        self.assertEquals('No executable found with that id in the database', response.json['message'])

        # Error raised because the testbed is off-line
        # We verify that the object is not in the db after creating it
        executable = Executable()
        executable.source_code_file = 'source'
        executable.compilation_script = 'script'
        executable.compilation_type = 'type'
        db.session.add(executable)
        db.session.commit()

        data = { 'executable_id' : 1,
                 'testbed_id' : 2 }

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(403, response.status_code)
        self.assertEquals('Testbed is off-line, this process needs to be performed manually', response.json['message'])

        # Verify that the executable was uploaded


        data = { 'executable_id' : 1,
                 'testbed_id' : 3 }

        response = self.client.post("/api/v1/deployments",
                                     data=json.dumps(data),
                                     content_type='application/json')
        self.assertEquals(201, response.status_code)
        self.assertEquals(1, response.json['executable_id'])
        self.assertEquals(3, response.json['testbed_id'])
        self.assertEquals(None, response.json['path'])
        self.assertEquals(None, response.json['status'])

        executable = db.session.query(Executable).filter_by(id=1).first()
        testbed = db.session.query(Testbed).filter_by(id=3).first()

        mock_upload_deployment.assert_called_with(executable, testbed)
    
    def test_post_and_patch_application_preprocessor(self):
        """
        It verifies the correct work of the method: post application prerocessor
        """

        data = {
            'name': 'app_name',
        }

        response = self.client.post("/api/v1/applications",
                                    data=json.dumps(data),
                                    content_type="application/json")
        
        self.assertEquals(201, response.status_code)
        application = response.json
        self.assertEquals('app_name', application['name'])

        data = {
            'name': 'app_name',
            'application_type': 'pepito'
        }

        response = self.client.post("/api/v1/applications",
                                    data=json.dumps(data),
                                    content_type="application/json")
        
        self.assertEquals(406, response.status_code)
        self.assertEquals(
          'Application type pepito not supported',
          response.json['message'])

        data = {
            'name': 'app_name',
            'application_type': 'MOULDABLE'
        }

        response = self.client.post("/api/v1/applications",
                                    data=json.dumps(data),
                                    content_type="application/json")
        
        self.assertEquals(201, response.status_code)
        application = response.json
        self.assertEquals('app_name', application['name'])
        self.assertEquals('MOULDABLE', application['application_type'])