# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from flask import Flask
from flask_testing import TestCase
from model.base import db
from model.application import Application
from model.models import Testbed, Node
import alde
import json

class AldeV1Tests(TestCase):
    """
    Test that verifies the REST API of Alde for its v1 version
    """

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        """
        It initializes the application
        """

        app = alde.create_app_v1(self.SQLALCHEMY_DATABASE_URI, 5101)

        return app

    def setUp(self):
        """
        It creates the memory db
        """

        db.create_all()

        # We store some Applications in the db for the tests
        application_1 = Application("AppName_1", "Path_1")
        application_2 = Application("AppName_2", "Path_2")
        db.session.add(application_1)
        db.session.add(application_2)

        # We store some testbeds in the db for the tests
        testbed_1 = Testbed("name_1", True, "slurm", "ssh", "user@server", ['slurm'])
        testbed_2 = Testbed("name_2", False, "slurm", "ssh", "user@server", ['slurm'])
        db.session.add(testbed_1)
        db.session.add(testbed_2)

        # We store some nodes in the db for the tests
        node_1 = Node("node_1", True)
        node_2 = Node("node_2", False)
        db.session.add(node_1)
        db.session.add(node_2)

        db.session.commit()

    def setDown(self):
        """
        Deletes everything in the memory db
        """

        db.session_remove()

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
        self.assertEquals('Path_1', application['path_to_code'])
        application = applications[1]
        self.assertEquals(2, application['id'])
        self.assertEquals('AppName_2', application['name'])
        self.assertEquals('Path_2', application['path_to_code'])

        # POST
        data={
                'name' : 'AppName_3',
                'path_to_code' : 'Path_3'
            }

        response = self.client.post('/api/v1/applications',
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        self.assertEquals('AppName_3', response.json['name'])
        self.assertEquals('Path_3', response.json['path_to_code'])
        self.assertEquals(3, response.json['id'])
        # We check that we only have three applicions
        response = self.client.get("/api/v1/applications")
        self.assertEquals(3, len(response.json['objects']))

        # GET Specific Entity
        response = self.client.get("/api/v1/applications/1")

        self.assertEquals(200, response.status_code)
        self.assertEquals('AppName_1', response.json['name'])
        self.assertEquals('Path_1', response.json['path_to_code'])
        self.assertEquals(1, response.json['id'])

        # DELETE
        response = self.client.delete("/api/v1/applications/1")

        self.assertEquals(204, response.status_code)
        # We check that we only have two applicions
        response = self.client.get("/api/v1/applications")
        self.assertEquals(2, len(response.json['objects']))

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
                'endpoint' : 'compiled_to_disk'
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
        # We check that we only have three testbeds
        response = self.client.get("/api/v1/testbeds")
        self.assertEquals(3, len(response.json['objects']))

        # GET Specific identity
        response = self.client.get("/api/v1/testbeds/3")
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
        self.assertEquals(2, len(response.json['objects']))

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
