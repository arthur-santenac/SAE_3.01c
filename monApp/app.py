import os
import sys
from flask import Flask
from flask_dropzone import Dropzone
from flask_bootstrap5 import Bootstrap

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # CORRECTION IMPORTANTE :
        # Comme tu inclus le dossier "monApp" dans l'EXE, il faut le préciser ici.
        return os.path.join(sys._MEIPASS, 'monApp', relative_path)
    # En mode développement
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

# --- Gestion du dossier de sauvegarde (Persistant) ---
if getattr(sys, 'frozen', False):
    # Si EXE : dossier à côté de l'exécutable
    application_path = os.path.dirname(sys.executable)
else:
    # Si DEV : dossier courant
    application_path = os.path.abspath(os.path.dirname(__file__))

# On crée le dossier s'il n'existe pas
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