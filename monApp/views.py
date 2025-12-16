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
    
        return render_template("configuration.html",title ="COHORT App")
        
    return "Format invalide", 400



@app.route("/configuration/", methods=["GET", "POST"])
def configuration():
    csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
    critères_pour_template = [] 
    if request.method == "POST":
        try:
            nb_groupes_str = request.form.get("nb-grp")
            if not nb_groupes_str:
                return render_template("configuration.html", title="COHORT App", error="Nombre de groupes requis.", critères=[])
            nb_groupes = int(nb_groupes_str)
            session["nb_groupes"] = nb_groupes
            if not os.path.exists(csv_path):
                return redirect(url_for("index"))
            liste_crit_brut = algo.recup_critere(csv_path)
            critères_pour_template = []
            dico_importance = {}
            for crit_brut in liste_crit_brut:
                crit_propre = crit_brut.lower().replace(" ", "_")
                form_field_name = "importance_" + crit_propre
                importance_value = int(request.form.get(form_field_name, 0))
                dico_importance[crit_brut] = importance_value 
                critères_pour_template.append(crit_propre)
            session["dico_importance"] = dico_importance
            if not os.path.exists(csv_path):
                return redirect(url_for("index")) 
            return redirect(url_for("repartition"))
        except ValueError:
            return render_template("configuration.html", title="COHORT App", error="Le nombre de groupes ou une des importances doit être un entier.", critères=critères_pour_template)
        except Exception as e:
            print(f"Une erreur est survenue: {e}") 
            return render_template("configuration.html", title="COHORT App", error=f"Une erreur est survenue: {e}", criteres=critères_pour_template)
    if os.path.exists(csv_path):
        liste_crit_brut = algo.recup_critere(csv_path)
        criteres_pour_template = []
        for critere in liste_crit_brut:
            criteres_pour_template.append(critere.lower().replace(" ", "_"))
    return render_template("configuration.html", title="COHORT App", criteres=criteres_pour_template)

@app.route("/repartition/")
def repartition():
    try:
        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        nombre_groupes = session.get("nb_groupes", 0)
        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        dico_importance = session["dico_importance"]
        groupes = algo.creer_groupe(liste_eleve, [], dico_importance, nombre_groupes)
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
            
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=nb_eleve_groupe,
                               nombre_groupes=nombre_groupes,groupes=groupes, score=score, place=place, prc_place=prc_place,
                               restants=restants,prc_restants=prc_restants,grp_genere=grp_genere, vert=vert)
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


