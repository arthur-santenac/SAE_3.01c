import os
import sys
from flask import Flask
from flask_dropzone import Dropzone
from flask_bootstrap5 import Bootstrap

app = Flask(__name__)

Bootstrap(app)

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('monApp'):
    upload_path = os.path.join(base_dir, 'monApp', 'static', 'uploads')
else:
    upload_path = os.path.join(base_dir, 'static', 'uploads')

if not os.path.exists(upload_path):
    os.makedirs(upload_path)

app.config.update(
    SECRET_KEY='2lzUl{$*D6#`8uXqlU.', 
    UPLOADED_PATH=upload_path,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.csv',
    DROPZONE_MAX_FILES=1,
)

dropzone = Dropzone(app)