import os
import sys
from flask import Flask
from flask_dropzone import Dropzone
from flask_bootstrap5 import Bootstrap

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.abspath(os.path.dirname(__file__))

upload_path = os.path.join(application_path, 'uploads_data')
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

app.config.update(
    SECRET_KEY='2lzUl{$*D6#`8uXqlU.',
    UPLOADED_PATH=upload_path,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.csv',
    DROPZONE_MAX_FILES=1,
)

Bootstrap(app)
dropzone = Dropzone(app)