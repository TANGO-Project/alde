# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


# Main ALDE Falsk start app...

import alde # pragma: no cover
from model.base import db # pragma: no cover

SQL_LITE_URL='sqlite:////tmp/test.db' # pragma: no cover
PORT=5000 # pragma: no cover

app = alde.create_app_v1(SQL_LITE_URL, PORT) # pragma: no cover

# We start the Flask loop
db.create_all() # pragma: no cover
# app.run()
