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
        # On essaie d'ouvrir le navigateur
        webbrowser.open(url)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du navigateur : {e}")

if __name__ == '__main__':
    # On affiche un message CLAIR dans le terminal pour l'utilisateur
    print("---------------------------------------------------")
    print("APPLICATION COHORT LANCEE")
    print("Si la page ne s'ouvre pas, cliquez ici : http://127.0.0.1:5000")
    print("---------------------------------------------------")

    # On lance le navigateur après 1.5 secondes (un peu plus long pour laisser Flask respirer)
    Timer(1.5, open_browser).start()
    
    # On lance le serveur
    app.run(host="127.0.0.1", port=5000, debug=False)