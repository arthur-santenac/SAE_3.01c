from flask import Flask, render_template, session, send_from_directory
from monApp.app import app;
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

@app.route('/telecharger')
def telecharger():
    liste_groupe = session.get('liste_groupe', None)
    if not liste_groupe:
        ...
    with open('static/uploads/groupes.csv', 'w', newline='') as fichier_csv:
        fichier_csv.write("num,nom,prenom")
        liste_critere = []
        for groupe in liste_groupe:
            if len(groupe) > 0:
                for critere in groupe[0].critere:
                    liste_critere.append(critere)
                    fichier_csv.write("," + critere)
                break
        fichier_csv.write(",groupe")
        for i in range(liste_groupe):
            for eleve in groupe:
                fichier_csv.write("\n")
                fichier_csv.write(str(eleve.num), eleve.nom, eleve.prenom)
                for un_critere in liste_critere:
                    fichier_csv.write(str(eleve.critere[un_critere]))
                fichier_csv.write(str(i))

    return send_from_directory(directory='static/uploads', path='groupes.csv', as_attachment=True)