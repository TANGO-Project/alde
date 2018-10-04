#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# ALDE PyBuilder script
#

from pybuilder.core import init, use_plugin

use_plugin("python.core")
use_plugin("python.unittest")
#use_plugin("python.coverage")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")
use_plugin("pypi:pybuilder_smart_copy_resources")
#use_plugin("python.sonarqube")

default_task = ["clean", "publish"]

# SonarQube configuration:
sonarqube_project_name = "tango-alde"
sonarqube_project_key = "ce9b5211cc48e2ca6ac94406eb8fe0a0f31eed06"

# Coverage configuration:
coverage_allow_non_imported_modules = "True"
coverage_exceptions = [ 'alde.py' ]

# Resources to be copied
@init
def set_properties(project):
    project.set_property("smart_copy_resources_basedir", ".")
    project.set_property("smart_copy_resources", {
        "alde_configuration.ini": "target/dist/alde-1.0.dev0/",
        "compilation_config.json": "target/dist/alde-1.0.dev0/",
        "logging_config.ini": "target/dist/alde-1.0.dev0/",
        "gpu_cards_list.json": "target/dist/alde-1.0.dev0/",
        "templates/compilation/*": "target/dist/alde-1.0.dev0/templates/compilation"
    })


@init
def initialize(project):
    project.build_depends_on('mockito')
    project.build_depends_on('Flask-Testing')
    project.build_depends_on('testfixtures')
    project.build_depends_on('requests')
    project.depends_on('python-dateutil')
    project.depends_on('sqlalchemy')
    project.depends_on('Flask')
    project.depends_on('Flask-Restless')
    project.depends_on('Flask-SQLAlchemy')
    project.depends_on('Flask-APScheduler')
    project.depends_on('flask-uploads')
    project.depends_on('simplejson')
    project.depends_on('flask-cors')
