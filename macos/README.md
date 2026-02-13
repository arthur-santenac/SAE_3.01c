# Sujet dunois SAE 3.01
- Arthur Santenac
- Louis Leray
- Hugo De Oliveira
- Paul Trojnar

# Ce que permet l'application

Actuellement, l'application permet à l'utilisateur d'importer un fichier dans le format .csv contenant les élèves à répartir. Il peut ensuite choisir le nombre de groupe et choisir le coéfficient de chaque critère (pour l'instant ils ne se modifient pas en fonction des valeurs du fichier). Les groupes sont ainsi crées et il peut ensuite les modifier manuellement.

# commande permettant de lancer l'application (linux/mac)

pip install -r requirements.txt
flask run

# si vs code ne trouve pas les imports

Appuyez sur Ctrl+Shift+P
Tapez "Python: Select Interpreter"
Choisissez l'interpréteur avec venv dans le chemin
