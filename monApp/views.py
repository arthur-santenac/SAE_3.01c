from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from monApp.app import app;
from monApp.static.util import algo
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

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
        file.save(os.path.join(UPLOAD_FOLDER, "groupes.csv"))
        return render_template("configuration.html",title ="COHORT App")
    return "Format de fichier non supporté", 400

@app.route('/configuration/')
def configuration():
    return render_template("configuration.html",title ="COHORT App")

@app.route('/repartition/')
def repartition():
    try:
        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        nombre_groupes = 12
        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        groupes = algo.creer_groupe(liste_eleve, [], algo.init_dico_importance(liste_eleve), nombre_groupes)
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes)
    except:
        print("test")
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=0,nombre_groupes=0,groupes=[[]])

@app.route('/exporter/')
def exporter():
    return render_template("exporter.html",title ="COHORT App")


