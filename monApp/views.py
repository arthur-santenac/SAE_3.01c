from flask import Flask, render_template, request, redirect, url_for, session, send_file
from monApp.app import app
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
            liste_crit_brut = algo.recup_critere(csv_path)
            nb_groupes = session.get("nb_groupes", 1)
            nouveaux_criteres_groupes = []
            for id_grp in range(1, nb_groupes + 1):
                for nom_crit in liste_crit_brut:
                    nom_input = f"chk_{id_grp}_{nom_crit}"
                    valeurs_cochees = request.form.getlist(nom_input)
                    nouveaux_criteres_groupes.append({'grp': id_grp, 'nom': nom_crit, 'valeurs': valeurs_cochees})
            session["criteres_groupes"] = nouveaux_criteres_groupes
            session.modified = True
            return redirect(url_for("repartition"))
    liste_crit_brut = algo.recup_critere(csv_path) if os.path.exists(csv_path) else []
    nouveaux_criteres = []
    for crit in session.get("criteres_groupes", []):
        if crit['nom'] in liste_crit_brut:
            nouveaux_criteres.append(crit)
    session["criteres_groupes"] = nouveaux_criteres
    criteres_pour_template = []
    for crit_brut in liste_crit_brut:
        format_propre = crit_brut.lower().replace(" ", "_")
        criteres_pour_template.append(format_propre)
    if os.path.exists(csv_path):
        dico_valeurs = {}
        for crit in liste_crit_brut:
            valeurs = algo.recup_ensemble_val_critere(crit, csv_path)
            dico_valeurs[crit] = valeurs
        session["liste_val_crit"] = dico_valeurs
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



@app.route("/repartition/", methods=["POST", "GET"])
def repartition():
    try:
        if request.method == "POST":
            dico_actuel = session.get("dico_importance", {})
            for critere in dico_actuel:
                if critere in request.form:
                    try:
                        dico_actuel[critere] = int(request.form[critere])
                    except ValueError:
                        pass
            session["dico_importance"] = dico_actuel
            session.modified = True
        print(session.get("dico_importance", {}))
        liste_eleve = algo.lire_fichier("monApp/static/uploads/groupes.csv")
        nombre_groupes = session.get("nb_groupes", 0)

        test_liste_critere = []
        if request.method == "POST":
            html_content = request.data.decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")

            modales = soup.find_all(class_="popup-card")

            for modale in modales:
                h3_tag = modale.find("h3")
                if not h3_tag:
                    continue

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
                    test_liste_critere.append(nouveau_critere)

        else:
            test_liste_critere = algo.test_creation_liste_critere()

        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        liste_nom_critere = algo.recup_critere("monApp/static/exemple/exemple2.csv")

        liste_criteres_valeur = []
        for critere in liste_nom_critere:
            liste_valeur_critere = algo.recup_ensemble_val_critere(
                critere, "monApp/static/exemple/exemple2.csv"
            )
            liste_criteres_valeur.append(liste_valeur_critere)

        dico_importance = session.get(
            "dico_importance", algo.init_dico_importance(liste_eleve)
        )

        groupes = algo.creer_groupe(
            liste_eleve, test_liste_critere, dico_importance, nombre_groupes
        )

        score = algo.score_totale(liste_eleve, groupes, dico_importance)

        place = str(len(liste_eleve) - len(groupes[-1])) + "/" + str(len(liste_eleve))
        prc_place = str((len(liste_eleve) - len(groupes[-1])) / len(liste_eleve) * 100)

        return render_template(
            "repartition.html",
            title="COHORT App",
            nb_eleve_groupe=nb_eleve_groupe,
            nombre_groupes=nombre_groupes,
            groupes=groupes,
            score=score,
            place=place,
            prc_place=prc_place,
            test_liste_critere=test_liste_critere,
            liste_criteres_valeur=liste_criteres_valeur,
            liste_nom_critere=liste_nom_critere,
            dico_importance=dico_importance
        )

    except Exception as e:
        print(f"Erreur dans repartition: {e}")
        import traceback

        traceback.print_exc()
        return render_template(
            "repartition.html",
            title="Erreur",
            nb_eleve_groupe=0,
            nombre_groupes=0,
            groupes=[[]],
            test_liste_critere=[],
            liste_criteres_valeur=[],
            liste_nom_critere=[],
        )


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
            restants.append(
                {
                    "num": cells[0],
                    "prenom": cells[1],
                    "nom": cells[2],
                    "criteres": cells[3:-1],
                }
            )
    groupes["restants"] = restants
    if groupes:
        with open(
            "monApp/static/uploads/groupes_finaux.csv", "w+", newline=""
        ) as fichier_csv:
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
        csv_path = os.path.join(
            app.root_path, "static", "uploads", "groupes_finaux.csv"
        )
        if not os.path.exists(csv_path):
            return "Fichier non trouvé", 404
        return send_file(
            csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name="liste_groupes.csv",
        )
