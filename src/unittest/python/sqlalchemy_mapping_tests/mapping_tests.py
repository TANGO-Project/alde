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
# Unit tests that checks ALDE SQL Alchemy integration
#

from flask import Flask
from flask_testing import TestCase
from models import db

class MappingTest(TestCase):
     """
     Common methods for all mapping test code
     """

     SQLALCHEMY_DATABASE_URI = "sqlite://"
     TESTING = True

     def create_app(self):
         """
         It initializes flask_testing
         """

         app = Flask(__name__)
         app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
         app.config['APP_PROFILE_FOLDER'] = '/profile_folder'
         db.init_app(app)
         db.app=app
         return app

     def setUp(self):
         """
         It creates the memory db
         """

         db.create_all()

     def setDown(self):
         """
         Deletes everything in the memory db
         """

         db.session_remove()
