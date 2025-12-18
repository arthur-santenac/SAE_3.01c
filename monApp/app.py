import os
from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from flask_bootstrap5 import Bootstrap

app = Flask (__name__)
# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

Bootstrap(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config.update(
    UPLOADED_PATH=os.path.join(os.path.dirname(__file__), "static", "uploads"),
    
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.csv',
    DROPZONE_MAX_FILES=1,    
   
)

dropzone = Dropzone(app)

