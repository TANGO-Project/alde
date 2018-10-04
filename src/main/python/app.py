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
# Flask application initialization and config loading
#


# Main ALDE Falsk start app...

import configparser
import alde # pragma: no cover
import logging # pragma: no cover
import file_upload.upload as upload
from logging.config import fileConfig # pragma: no cover
from models import db # pragma: no cover

# Loading logger configuration
fileConfig('logging_config.ini') # pragma: no cover
logger = logging.getLogger() # pragma: no cover

def load_config():
    """
    Functions that loads ALDE configuration from file
    It is specting a file alde_configuration.ini in the same location
    than the main executable
    """

    logger.info("Loading configuration")
    config = configparser.ConfigParser()
    config.read('alde_configuration.ini')
    default = config['DEFAULT']
    print(default)
    app_types = [e.strip() for e in default['APP_TYPES'].split(',')]

    conf = {
        'SQL_LITE_URL' : default['SQL_LITE_URL'],
        'PORT' : default['PORT'],
        'APP_UPLOAD_FOLDER' : default['APP_UPLOAD_FOLDER'],
        'APP_PROFILE_FOLDER' : default['APP_PROFILE_FOLDER'],
        'APP_TYPES' : app_types,
        'COMPARATOR_PATH' : default['COMPARATOR_PATH'],
        'COMPARATOR_FILE' : default['COMPARATOR_FILE']
    }

    return conf

def main(): # pragma: no cover
    """
    Main function that starts the ALDE Flask Service
    """

    conf = load_config() # pragma: no cover

    logger.info("Starting ALDE") # pragma: no cover
    app = alde.create_app_v1(conf['SQL_LITE_URL'], 
                             conf['PORT'], 
                             conf['APP_UPLOAD_FOLDER'], 
                             conf['APP_PROFILE_FOLDER'], 
                             conf['APP_TYPES'],
                             conf['COMPARATOR_PATH'],
                             conf['COMPARATOR_FILE'] ) # pragma: no cover

    # We start the Flask loop
    db.create_all() # pragma: no cover

    # We register the upload url
    upload_prefix = alde.url_prefix_v1 + "/upload"
    app.register_blueprint(upload.upload_blueprint, url_prefix=upload_prefix)

    app.run(use_reloader=False)

if __name__ == '__main__':
    main()
