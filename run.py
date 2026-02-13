import sys
import os
import webbrowser
from threading import Timer

# Ajout du chemin pour trouver les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monApp.app import app
import monApp.views 

def open_browser():
    url = "http://127.0.0.1:5000"
    print(f"--> Tentative d'ouverture automatique de : {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du navigateur : {e}")

if __name__ == '__main__':

    Timer(1.5, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)