from flask import Flask, request, redirect, url_for, render_template
from monApp.app import app;
from monApp.static.util.algo import groupes,nb_eleve_groupe
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
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return "Fichier importé avec succès"
    return "Format de fichier non supporté", 400

@app.route('/configuration/')
def configuration():
    return render_template("configuration.html",title ="R3.01 Dev Web avec yannnis ")

nombre_groupes = len(nb_eleve_groupe)

@app.route('/repartition/')
def repartition():
    return render_template("repartition.html",title ="R3.01 Dev Web avec yannnis ",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes)

@app.route('/exporter/')
def exporter():
    return render_template("exporter.html",title ="R3.01 Dev Web avec yannnis ")





