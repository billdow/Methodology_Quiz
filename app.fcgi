#!/usr/bin/python3

import sys
import os

# Add your application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up the virtual environment
activate_this = os.path.dirname(__file__) + '/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

from flup.server.fcgi import WSGIServer
from app import app

if __name__ == '__main__':
    WSGIServer(app).run()
