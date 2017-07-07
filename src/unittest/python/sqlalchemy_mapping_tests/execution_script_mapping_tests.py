# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.models import ExecutionScript
from model.base import db

class ExecutionScriptMappingTest(MappingTest):
    """
    Series of test to validate the correct mapping to the class
    ExecutionScript to be stored into an SQL relational db
    """

    def test_crud_execution_script(self):
        """It test basic CRUD operations of an ExecutionScript Class"""

        # We verify that the object is not in the db after creating
        execution_script = ExecutionScript("ls", "slurm:sbatch", "-X")
        self.assertIsNone(execution_script.id)

        # We store the object in the db
        db.session.add(execution_script)

        # We recover the execution_script from the db
        execution_script = db.session.query(ExecutionScript).filter_by(command='ls').first()
        self.assertIsNotNone(execution_script.id)
        self.assertEquals("ls", execution_script.command)
        self.assertEquals("slurm:sbatch", execution_script.execution_type)
        self.assertEquals("-X", execution_script.parameters)

        # We check that we can update the application
        execution_script.parameters = '-X1'
        db.session.commit()
        execution_script_2 = db.session.query(ExecutionScript).filter_by(command='ls').first()
        self.assertEquals(execution_script.id, execution_script_2.id)
        self.assertEquals("-X1", execution_script.parameters)

        # We check the deletion
        db.session.delete(execution_script_2)
        count = db.session.query(ExecutionScript).filter_by(command='ls').count()
        self.assertEquals(0, count)