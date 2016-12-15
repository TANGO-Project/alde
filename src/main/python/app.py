# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


# Main ALDE Falsk start app...

import alde
from model.base import db

SQL_LITE_URL='sqlite:////tmp/test.db'
PORT=5000

app = alde.create_app_v1(SQL_LITE_URL, PORT)

# We start the Flask loop
db.create_all() ## I will probably need to look at this more carefully...
# app.run()
