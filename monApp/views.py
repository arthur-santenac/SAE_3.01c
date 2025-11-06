from flask import Flask
from monApp.app import app;
from flask import render_template, request
from flask import render_template
from monApp.static.util import eleve, critere
from monApp.static.util.algo import nb_eleve_groupe, groupes

@app.route('/')
@app.route('/importer/')
def importer():
    return render_template("importer.html",title ="R3.01 Dev Web avec yannnis ")

@app.route('/configuration/')
def configuration():
    return render_template("configuration.html",title ="R3.01 Dev Web avec yannnis ")

nombre_groupes = len(nb_eleve_groupe)

@app.route('/repartition/')
def repartition():
    return render_template("repartition.html",title ="R3.01 Dev Web avec yannnis ",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes)
