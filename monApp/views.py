from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from monApp.app import app;
from monApp.static.util import algo
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

@app.route("/")
def index():
    return render_template("importer.html")

@app.route("/importer/", methods=["POST"])
def importer():
    if "csv_file" not in request.files:
        return "Aucun fichier sélectionné", 400
    file = request.files["csv_file"]
    if file.filename == "":
        return "Nom de fichier vide", 400
    if file and file.filename.endswith(".csv"):
        file.save(os.path.join(UPLOAD_FOLDER, "groupes.csv"))
        return redirect(url_for("configuration"))
    return "Format de fichier non supporté", 400



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
                dico_importance[crit_propre] = importance_value 
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
        groupes = algo.creer_groupe(liste_eleve, [], session.get("dico_importance"), nombre_groupes)
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=nb_eleve_groupe,nombre_groupes=nombre_groupes,groupes=groupes)
    except:
        return render_template("repartition.html",title ="COHORT App",nb_eleve_groupe=0,nombre_groupes=0,groupes=[[]])

@app.route("/exporter")
def exporter():
    liste_groupe = ...
    if not liste_groupe:
        ...
    with open("static/uploads/groupes.csv", "w", newline="") as fichier_csv:
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
    return send_from_directory(directory="static/uploads", path="groupes.csv", as_attachment=True)