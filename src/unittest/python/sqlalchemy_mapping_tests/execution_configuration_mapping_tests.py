# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, ExecutionConfiguration, Testbed, Execution

class ExecutionConfigurationMappingTest(MappingTest):
    """
    Series of test to validate the correct mapping to the class
    ExecutionConfiguration to be stored into an SQL relational db
    """

    def test_crud_execution_configuration(self):
        """It test basic CRUD operations of an ExecutionConfiguration Class"""

        # We verify that the object is not in the db after creating
        execution_configuration = ExecutionConfiguration()
        execution_configuration.execution_type = "slurm:sbatch"
        self.assertIsNone(execution_configuration.id)

        # We store the object in the db
        db.session.add(execution_configuration)

        # We recover the execution_configuration from the db
        execution_configuration = db.session.query(ExecutionConfiguration).filter_by(execution_type='slurm:sbatch').first()
        self.assertIsNotNone(execution_configuration.id)
        self.assertEquals("slurm:sbatch", execution_configuration.execution_type)

        # We check that we can update the application
        execution_configuration.execution_type = 'slurm:singularity'
        db.session.commit()
        execution_configuration_2 = db.session.query(ExecutionConfiguration).filter_by(execution_type='slurm:singularity').first()
        self.assertEquals(execution_configuration.id, execution_configuration_2.id)
        self.assertEquals("slurm:singularity", execution_configuration.execution_type)

        # We check the deletion
        db.session.delete(execution_configuration_2)
        count = db.session.query(ExecutionConfiguration).filter_by(execution_type='slurm:singularity').count()
        self.assertEquals(0, count)

    def test_relation_with_testbed(self):
        """It check it is possible to relate the application with the testbed"""

        # We create first a testbed and commit it to the db
        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])

        db.session.add(testbed)
        db.session.commit()

        # We create an execution script
        execution_configuration = ExecutionConfiguration()
        execution_configuration.execution_type = "slurm:sbatch"
        execution_configuration.testbed = testbed

        db.session.add(execution_configuration)
        db.session.commit()

        # We retrieve the execution script from the db
        execution_configuration = db.session.query(ExecutionConfiguration).filter_by(execution_type='slurm:sbatch').first()
        self.assertEquals("name", execution_configuration.testbed.name)
        self.assertEquals(testbed.id, execution_configuration.testbed.id)
