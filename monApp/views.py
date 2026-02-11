from flask import render_template, request, redirect, url_for, session, send_file
from monApp.app import app
from monApp.static.util import algo
import os
from bs4 import BeautifulSoup
import csv
import traceback
import json

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")


@app.route("/")
def index():
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "groupes.csv")):
        os.remove(os.path.join(UPLOAD_FOLDER, "groupes.csv"))
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "groupes_finaux.csv")):
        os.remove(os.path.join(UPLOAD_FOLDER, "groupes_finaux.csv"))
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "configuration.json")):
        os.remove(os.path.join(UPLOAD_FOLDER, "configuration.json"))
    return render_template("importer.html")

@app.route("/importerCSV/", methods=["POST"])
def importerCSV():
    if "file" not in request.files:
        return "Aucun fichier", 400
    file = request.files.get("file")
    if file and file.filename.endswith(".csv"):
        save_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
        file.save(save_path)

        json_path = os.path.join(UPLOAD_FOLDER, "configuration.json")
        if os.path.exists(json_path):
            os.remove(json_path)

        session.pop("dico_importance", None)
        session.pop("criteres_groupes", None)
        session.pop("nb_groupes", None)
        session["valide"] = False
        
        return redirect(url_for("configuration"))
    return "Format invalide", 400

@app.route("/importerJSON/", methods=["POST"])
def importerJSON():
    if "file" not in request.files:
        return "Aucun fichier", 400
    file = request.files.get("file")
    if file and file.filename.endswith(".json"):
        save_path = os.path.join(UPLOAD_FOLDER, "configuration.json")
        file.save(save_path)

        session.pop("dico_importance", None)
        session.pop("criteres_groupes", None)
        session.pop("nb_groupes", None)
        
        return redirect(url_for("configuration"))
    return "Format invalide", 400

@app.route("/configuration/", methods=["GET", "POST"])
def configuration():
    csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
    json_path = os.path.join(UPLOAD_FOLDER, "configuration.json")
    liste_crit_brut = algo.recup_critere(csv_path) if os.path.exists(csv_path) else []
    
    dico_importance = None
    criteres_groupes = None

    if session.get("dico_importance") and session.get("criteres_groupes"):
        dico_importance = session.get("dico_importance")
        criteres_groupes = session.get("criteres_groupes")
        nb_groupes = session.get("nb_groupes", 1)
        
    elif request.method == "GET" and os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config_json = json.load(f)
            dico_importance = config_json.get("dico_importance")
            criteres_groupes = config_json.get("liste_critere") 
            nb_groupes = config_json.get("nb_groupes", 1)
            session["valide"] = True
        except Exception as e:
            print(f"Erreur lecture JSON: {e}")

    if dico_importance is None and os.path.exists(csv_path):
        liste_eleve_temp = algo.lire_fichier(csv_path)
        dico_importance = algo.init_dico_importance(liste_eleve_temp)
        nb_groupes = 1
        criteres_groupes = []
        for nom_crit in liste_crit_brut:
            valeurs_possibles = list(algo.recup_ensemble_val_critere(nom_crit, csv_path))
            criteres_groupes.append({'grp': 1, 'nom': nom_crit, 'valeurs': valeurs_possibles})
        session["valide"] = False
    session["dico_importance"] = dico_importance
    session["criteres_groupes"] = criteres_groupes
    session["nb_groupes"] = nb_groupes
    session["liste_ind_groupes"] = list(range(1, nb_groupes + 1))
    if request.method == "POST":
        action = request.form.get("btn")
        if dico_importance:
            for crit_nom in dico_importance:
                crit_propre = crit_nom.lower().replace(" ", "_")
                nom_input = f"importance_{crit_propre}"
                valeur = request.form.get(nom_input)
                if valeur:
                    dico_importance[crit_nom] = int(valeur)
            session["dico_importance"] = dico_importance
        if action == "btn-valide":
            nb_groupes_str = request.form.get("nb-grp")
            if nb_groupes_str:
                nb_int = int(nb_groupes_str)
                session["nb_groupes"] = nb_int
                session["valide"] = True
                session["liste_ind_groupes"] = list(range(1, nb_int + 1))
                tous_les_criteres = []
                for id_grp in range(1, nb_int + 1):
                    for nom_crit in liste_crit_brut:
                        valeurs_possibles = list(algo.recup_ensemble_val_critere(nom_crit, csv_path))
                        tous_les_criteres.append({'grp': id_grp, 'nom': nom_crit, 'valeurs': valeurs_possibles})
                session["criteres_groupes"] = tous_les_criteres
        elif action == "btn-repartition":
            nouveaux_criteres_groupes = []
            nb_actuel = session.get("nb_groupes", 1)
            for id_grp in range(1, nb_actuel + 1):
                for nom_crit in liste_crit_brut:
                    nom_input = f"chk_{id_grp}_{nom_crit}"
                    valeurs_cochees = request.form.getlist(nom_input)
                    nouveaux_criteres_groupes.append({'grp': id_grp, 'nom': nom_crit, 'valeurs': valeurs_cochees})
            session["criteres_groupes"] = nouveaux_criteres_groupes
            session.modified = True
            return redirect(url_for("repartition"))
    criteres_propres_session = []
    if session.get("criteres_groupes"):
        for crit in session["criteres_groupes"]:
            if crit['nom'] in liste_crit_brut:
                criteres_propres_session.append(crit)
    session["criteres_groupes"] = criteres_propres_session
    criteres_pour_template = []
    map_importance = {}
    for crit_brut in liste_crit_brut:
        format_propre = crit_brut.lower().replace(" ", "_")
        criteres_pour_template.append(format_propre)
        if dico_importance and crit_brut in dico_importance:
            map_importance[format_propre] = dico_importance[crit_brut]
    if os.path.exists(csv_path):
        dico_valeurs = {}
        for crit in liste_crit_brut:
            dico_valeurs[crit] = algo.recup_ensemble_val_critere(crit, csv_path)
        session["liste_val_crit"] = dico_valeurs
    return render_template("configuration.html", 
        title="COHORT App", 
        criteres=criteres_pour_template, 
        valide=session.get("valide"), 
        liste_grp=session.get("liste_ind_groupes", []),
        criteres_choisis=session.get("criteres_groupes", []), 
        nb_grp=session.get("nb_groupes", 1),
        map_importance=map_importance
    )

@app.route("/repartition/", methods=["POST", "GET"])
def repartition():
    try:
        dico_importance = session.get("dico_importance", {})
        liste_critere = []

        if request.method == "POST":
            html_content = request.data.decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")
            nouveau_dico = dico_importance.copy()
            for critere_nom in nouveau_dico.keys():
                input_tag = soup.find("input", {"name": critere_nom, "type": "number"})
                if input_tag and input_tag.get("value"):
                    try:
                        nouveau_dico[critere_nom] = int(input_tag.get("value"))
                    except ValueError:
                        pass

            session["dico_importance"] = nouveau_dico
            dico_importance = nouveau_dico
            criteres_pour_session = []

            modales = soup.find_all(class_="popup-card")
            for modale in modales:
                h3_tag = modale.find("h3")
                if not h3_tag: continue
                titre_groupe = h3_tag.get_text()
                num_groupe = int("".join(filter(str.isdigit, titre_groupe)))
                criteres_temp = {}
                all_inputs = modale.find_all("input", {"type": "checkbox"})
                for chk in all_inputs:
                    if chk.has_attr("checked"):
                        nom_crit = chk.get("name")
                        valeur = chk.get("value")
                        if nom_crit:
                            if nom_crit not in criteres_temp:
                                criteres_temp[nom_crit] = []
                            criteres_temp[nom_crit].append(valeur)
                for nom, valeurs in criteres_temp.items():
                    nouveau_critere = algo.critere.Critere(num_groupe, valeurs, nom)
                    liste_critere.append(nouveau_critere)
                    criteres_pour_session.append({
                        'grp': num_groupe, 
                        'nom': nom, 
                        'valeurs': valeurs
                    })
            session["criteres_groupes"] = criteres_pour_session
            session.modified = True

        else:
            liste_critere=[]
            for critere in session["criteres_groupes"]:
                liste_critere.append(algo.critere.Critere(critere['grp'],critere['valeurs'],critere['nom']))
            liste_eleve_temp = algo.lire_fichier("monApp/static/uploads/groupes.csv")
            if not dico_importance:
                dico_importance = algo.init_dico_importance(liste_eleve_temp)
                session["dico_importance"] = dico_importance

        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        nombre_groupes = session.get("nb_groupes", 0)

        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        liste_nom_critere = algo.recup_critere("monApp/static/uploads/groupes.csv")

        liste_criteres_valeur = []
        for critere in liste_nom_critere:
            liste_valeur_critere = algo.recup_ensemble_val_critere(critere, "monApp/static/uploads/groupes.csv")
            liste_criteres_valeur.append(liste_valeur_critere)

        groupes = algo.creer_groupe(liste_eleve, liste_critere, dico_importance, nombre_groupes)
        score = algo.score_totale(liste_eleve, groupes, dico_importance)

        place = str(len(liste_eleve) - len(groupes[-1])) + "/" + str(len(liste_eleve))
        try:
            prc_place = str((len(liste_eleve) - len(groupes[-1])) / len(liste_eleve) * 100)
        except ZeroDivisionError:
            prc_place = "0"
        bleu = len(liste_eleve) - len(groupes[-1]) == len(liste_eleve)

        return render_template(
            "repartition.html",
            title="COHORT App",
            nb_eleve_groupe=nb_eleve_groupe,
            nombre_groupes=nombre_groupes,
            groupes=groupes,
            score=score,
            place=place,
            prc_place=prc_place,
            liste_critere=liste_critere,
            liste_criteres_valeur=liste_criteres_valeur,
            liste_nom_critere=liste_nom_critere,
            dico_importance=dico_importance,
            bleu=bleu
        )

    except Exception as e:
        print(f"Erreur dans repartition: {e}")
        traceback.print_exc()
        return render_template("repartition.html", error="Une erreur est survenue")


@app.route("/exporter_groupes", methods=["POST"])
def exporter_groupes():
    html_content = request.data.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    groupes = {}
    for idx, table in enumerate(soup.select("#eleves_classes .liste-eleves")):
        groupe_nom = f"groupe_{idx + 1}"
        eleves = []
        for row in table.select("tr.eleve"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
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
    for row in soup.select("#eleves_restants .liste-eleves tr.eleve"):
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) >= 2:
            restants.append({
                "num": cells[0],
                "prenom": cells[1],
                "nom": cells[2],
                "criteres": cells[3:-1],
            })
    groupes["restants"] = restants
    if groupes:
        with open("monApp/static/uploads/groupes_finaux.csv", "w+",
                  newline="", encoding="utf-8") as fichier_csv:
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
                    criteres_eleve = eleve.get("criteres",
                                               eleve.get("critere", []))
                    for val in criteres_eleve:
                        ligne.append(val)
                    ligne.append(groupe_id)
                    writer.writerow(ligne)
                groupe_id += 1
        csv_path = os.path.join(app.root_path, "static", "uploads",
                                "groupes_finaux.csv")
        if not os.path.exists(csv_path):
            return "Fichier non trouvé", 404
        return send_file(
            csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name="liste_groupes.csv",
        )
    
@app.route("/exporter_config/", methods=["GET"])
def exporter_config():
    nb_groupes = session.get("nb_groupes")
    dico_importance = session.get("dico_importance", {})
    criteres_groupes = session.get("criteres_groupes", [])

    config_data = {
        "nb_groupes": nb_groupes,
        "dico_importance": dico_importance,
        "liste_critere": criteres_groupes
    }

    json_path = os.path.join(UPLOAD_FOLDER, "configuration.json")

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
            
        return send_file(
            json_path,
            mimetype="application/json",
            as_attachment=True,
            download_name="configuration.json",
        )
    except Exception as e:
        return "Erreur lors de la création du fichier de configuration", 500