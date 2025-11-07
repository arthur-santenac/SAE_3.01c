from flask import Flask, render_template, request, redirect, url_for, session
from monApp.app import app  # Point-virgule inutile supprimé
import os
from monApp.static.util import algo 

# SUPPRIMÉE: La ligne ci-dessous causait l'erreur, car 'groupes' et 'nb_eleve_groupe'
# ne sont créés que DANS la route 'configuration', pas au démarrage.
# from monApp.static.util.algo import groupes,nb_eleve_groupe 

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# AJOUTÉ: Une clé secrète est OBLIGATOIRE pour utiliser les sessions Flask
app.secret_key = 'remplacez-moi-par-une-vraie-cle-secrete'

@app.route('/')
def index():
    return render_template('importer.html')

@app.route('/importer/', methods=['POST'])
def importer():
    if 'csv_file' not in request.files:
        return "Aucun fichier sélectionné", 400
    file = request.files['csv_file']
    if file.filename == '':
        return "Nom de fichier vide", 400
    if file and file.filename.endswith('.csv'):
        # Assurons-nous que le dossier existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
        file.save(os.path.join(UPLOAD_FOLDER, "groupes.csv"))
        
        # MODIFIÉ: Il est préférable de rediriger après un POST
        # plutôt que de rendre un template directement.
        return redirect(url_for('configuration'))
    
    return "Format de fichier non supporté", 400

@app.route('/configuration/', methods=['GET', 'POST'])
def configuration():
    if request.method == 'POST':
        try:
            nb_groupes_str = request.form.get('nb-grp')
            if not nb_groupes_str:
                return render_template("configuration.html", title="COHORT App", error="Nombre de groupes requis.")
            nb_groupes = int(nb_groupes_str)

            dico_importance = {
                "genre": int(request.form.get('importance_genre', 0)),
                "niveau Français": int(request.form.get('importance_francais', 0)),
                "niveau Maths": int(request.form.get('importance_maths', 0)),
                "Pénibilité": int(request.form.get('importance_penibilite', 0))
            }

            liste_critere_constraints = []

            csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
            if not os.path.exists(csv_path):
                return redirect(url_for('index')) 
            liste_eleve = algo.lire_fichier(csv_path)
            groupes_obj = algo.creer_groupe(liste_eleve, liste_critere_constraints, dico_importance, nb_groupes)

            score = algo.score_totale(liste_eleve, groupes_obj, dico_importance)
            nb_eleve_groupe = [len(g) for g in groupes_obj]
            
            groupes_serialisables = []
            for groupe in groupes_obj:
                groupe_serial = []
                for elev in groupe:
                    groupe_serial.append({
                        "num": elev.num,  
                        "nom": elev.nom,
                        "prenom": elev.prenom,
                        "critere": elev.critere
                    })
                groupes_serialisables.append(groupe_serial)

            session['results'] = {
                'groupes': groupes_serialisables,
                'nb_eleve_groupe': nb_eleve_groupe,
                'nombre_groupes': len(nb_eleve_groupe), 
                'score': score
            }
            return redirect(url_for('repartition'))

        except ValueError:
            return render_template("configuration.html", title="COHORT App", error="Le nombre de groupes doit être un entier.")
        except Exception as e:
            print(f"Une erreur est survenue: {e}") 
            return render_template("configuration.html", title="COHORT App", error=f"Une erreur est survenue: {e}")
    return render_template("configuration.html", title="COHORT App")


@app.route('/repartition/')
def repartition():
    results = session.get('results', None)
    
    if not results:
        return redirect(url_for('configuration'))

    return render_template("repartition.html", title="COHORT App - Répartition", nb_eleve_groupe=results['nb_eleve_groupe'],nombre_groupes=results['nombre_groupes'],
                           groupes=results['groupes'],
                           score=results.get('score', 0))



# Le code suivant était en double et utilisait des variables
# globales qui n'existent plus.
#
# nombre_groupes = len(nb_eleve_groupe)
#
# @app.route('/repartition/')
# def repartition():
#     return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes)
#


@app.route('/exporter/')
def exporter():
    return render_template("exporter.html",title ="COHORT App")