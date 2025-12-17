from flask import Flask, render_template, request, redirect, url_for, session, send_file
from monApp.app import app;
from monApp.static.util import algo
import os
from flask import request
from bs4 import BeautifulSoup
import csv

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

@app.route("/")
def index():
    return render_template("importer.html")

@app.route("/importer/", methods=["POST"])
def importer():
    if "file" not in request.files:
        return "Aucun fichier", 400
    file = request.files.get("file")
    if file and file.filename.endswith(".csv"):
        save_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
        file.save(save_path)
        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        session["criteres_groupes"] = [] 
        session["valide"] = False
        session["dico_importance"] = algo.init_dico_importance(liste_eleve)
        return render_template("configuration.html",title ="COHORT App")
    return "Format invalide", 400


@app.route("/configuration/", methods=["GET", "POST"])
def configuration():
    csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
    if "criteres_groupes" not in session:
        session["criteres_groupes"] = []
    if "valide" not in session:
        session["valide"] = False

    if request.method == "GET":
        session["valide"] = False
        session["nb_groupes"] = 1
        session["criteres_groupes"] = []

    
    if request.method == "POST":
        action = request.form.get("btn")
        if action == "btn-valide":
            nb_groupes_str = request.form.get("nb-grp")
            if nb_groupes_str:
                nb_int = int(nb_groupes_str)
                session["nb_groupes"] = nb_int
                session["valide"] = True
                session["liste_ind_groupes"] = list(range(1, nb_int + 1))
                liste_crit_brut = algo.recup_critere(csv_path)
                tous_les_criteres = []
                
                for id_grp in range(1, nb_int + 1):
                    for nom_crit in liste_crit_brut:
                        valeurs_possibles = list(algo.recup_ensemble_val_critere(nom_crit, csv_path))
                        tous_les_criteres.append({'grp': id_grp, 'nom': nom_crit, 'valeurs': valeurs_possibles})
                session["criteres_groupes"] = tous_les_criteres
        elif action == "btn-repartition":
            return redirect(url_for("repartition"))

    liste_crit_brut = algo.recup_critere(csv_path) if os.path.exists(csv_path) else []
    nouveaux_criteres = []
    for c in session.get("criteres_groupes", []):
        if c['nom'] in liste_crit_brut:
            nouveaux_criteres.append(c)
    session["criteres_groupes"] = nouveaux_criteres
    criteres_pour_template = []
    for c in liste_crit_brut:
        format_propre = c.lower().replace(" ", "_")
        criteres_pour_template.append(format_propre)
    if os.path.exists(csv_path):
        session["liste_val_crit"] = {crit: algo.recup_ensemble_val_critere(crit, csv_path) for crit in liste_crit_brut}
    return render_template("configuration.html", title="COHORT App", criteres=criteres_pour_template, valide=session.get("valide"), liste_grp=session.get("liste_ind_groupes", []),
        criteres_choisis=session.get("criteres_groupes", []), nb_grp=session.get("nb_groupes", 1))

@app.route("/configuration/add_crit/<int:grp_id>", methods=["GET", "POST"])
def ajout_crit_grp(grp_id):
    liste_val_crit = session.get("liste_val_crit", {})
    crit_selectionne = request.args.get("crit_nom")
    if request.method == "POST":
        nom_crit_final = request.form.get("crit_nom")
        valeurs_choisies = request.form.getlist("valeurs")
        if nom_crit_final and valeurs_choisies:
            temp_criteres = session.get("criteres_groupes", [])
            temp_criteres.append({'grp': grp_id, 'nom': nom_crit_final, 'valeurs': valeurs_choisies})
            session["criteres_groupes"] = temp_criteres
            return redirect(url_for("configuration"))
    return render_template("ajout_critere.html", title="Ajouter un critère", grp_id=grp_id, liste_val_crit=liste_val_crit, crit_selectionne=crit_selectionne)


@app.route("/configuration/criteres", methods=["GET", "POST"])
def configuration_critere():
    liste_crit= request.args.getlist("liste_crit")
    est_valide = session.get("valide", False) 
    ind_grp = session.get("liste_ind_groupes", [])
    nb_groupes = session.get("nb_groupes",1)
    return render_template("configuration.html", title="COHORT App", criteres= liste_crit, valide = est_valide, liste_grp = ind_grp, nb_grp = nb_groupes)




@app.route("/repartition/")
def repartition():
    try:
        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        nombre_groupes = session.get("nb_groupes", 0)
        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        dico_importance = session["dico_importance"]
        liste_objets_criteres = []
        for crit in session.get("criteres_groupes", []):
            liste_objets_criteres.append(algo.critere.Critere(crit['grp'], crit['valeurs'], crit['nom']))
        groupes = algo.creer_groupe(liste_eleve, liste_objets_criteres, dico_importance, nombre_groupes)
        score = algo.score_totale(liste_eleve, groupes, session["dico_importance"])
        place = str(len(liste_eleve) - len(groupes[-1])) + "/" + str(len(liste_eleve))
        prc_place = str((len(liste_eleve) - len(groupes[-1])) / len(liste_eleve) * 100)
        restants = str(len(groupes[-1]))
        prc_restants = str(len(groupes[-1]) / len(liste_eleve) * 100)
        grp_genere = str(len(groupes) - 1)
        if (len(groupes[-1]) > 0):
            vert= False
            grp_genere += " + 1"
        else:
            vert = True
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes, score=score, 
                               place=place, prc_place=prc_place, restants=restants,prc_restants=prc_restants,grp_genere=grp_genere, vert=vert)
    except:
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=0,nombre_groupes=0,groupes=[[]])

@app.route('/exporter_groupes', methods=['POST'])
def exporter_groupes():
    html_content = request.data.decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    groupes = {}
    for idx, table in enumerate(soup.select('#eleves_classes .liste-eleves')):
        groupe_nom = f"groupe_{idx + 1}"
        eleves = []
        for row in table.select('tr.eleve'):
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if len(cells) >= 2:
                eleve = {
                    "num": cells[0],
                    "prenom": cells[1],
                    "nom": cells[2],
                    "criteres": cells[3:-1],
                }
                eleves.append(eleve)
        groupes[groupe_nom] = eleves
    restants = []
    for row in soup.select('#eleves_restants .liste-eleves tr.eleve'):
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if len(cells) >= 2:
            restants.append({
                "num": cells[0],
                "prenom": cells[1],
                "nom": cells[2],
                "criteres": cells[3:-1],
            })
    groupes["restants"] = restants
    if groupes:
        with open("monApp/static/uploads/groupes_finaux.csv", "w+", newline="") as fichier_csv:
            writer = csv.writer(fichier_csv)
            liste_critere = []
            for groupe in groupes.values():
                if len(groupe) > 0:
                    liste_critere = groupe[0].get("criteres", []) 
                    break
            header = ["num", "nom", "prenom"] + liste_critere + ["groupe"]
            writer.writerow(header)
            groupe_id = 1
            for groupe in groupes.values():
                for eleve in groupe:
                    ligne = []
                    ligne.append(eleve.get("num", "")) 
                    ligne.append(eleve.get("nom", ""))
                    ligne.append(eleve.get("prenom", ""))
                    criteres_eleve = eleve.get("criteres", eleve.get("critere", []))
                    for val in criteres_eleve:
                        ligne.append(val)
                    ligne.append(groupe_id)
                    writer.writerow(ligne)
                groupe_id += 1
        csv_path = os.path.join(app.root_path, 'static', 'uploads', 'groupes_finaux.csv')
        if not os.path.exists(csv_path):
            return "Fichier non trouvé", 404
        return send_file(csv_path, mimetype="text/csv", as_attachment=True, download_name="liste_groupes.csv")


