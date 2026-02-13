from flask import render_template, request, redirect, url_for, session, send_file
from monApp.app import app
from monApp.static.util import algo
import os
import csv
import json
import traceback
import json
from flask import jsonify

UPLOAD_FOLDER = app.config['UPLOADED_PATH']



@app.route("/")
def index():
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "groupes.csv")):
        os.remove(os.path.join(UPLOAD_FOLDER, "groupes.csv"))
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "groupes_finaux.csv")):
        os.remove(os.path.join(UPLOAD_FOLDER, "groupes_finaux.csv"))
    if os.path.exists(os.path.join(UPLOAD_FOLDER, "configuration.json")):
        os.remove(os.path.join(UPLOAD_FOLDER, "configuration.json"))
    return render_template("importer.html")


@app.route("/importe_csv/", methods=["POST"])
def importe_csv():
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
        
        return render_template("configuration.html", title="COHORT App")
    return "Format invalide", 400


@app.route("/importer_json/", methods=["POST"])
def importer_json():
    if "file" not in request.files:
        return "Aucun fichier", 400
    file = request.files.get("file")
    if file and file.filename.endswith(".json"):
        save_path = os.path.join(UPLOAD_FOLDER, "configuration.json")
        file.save(save_path)

        session.pop("dico_importance", None)
        session.pop("criteres_groupes", None)
        session.pop("nb_groupes", None)
        
        return render_template("configuration.html", title="COHORT App")
    return "Format invalide", 400


@app.route("/configuration/", methods=["GET", "POST"])
def configuration():
    try:
        # 1. Définition des chemins
        csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
        json_path = os.path.join(UPLOAD_FOLDER, "configuration.json")
        
        # 2. Récupération des critères bruts
        liste_crit_brut = algo.recup_critere(csv_path) if os.path.exists(csv_path) else []
        
        dico_importance = None
        criteres_groupes = None

        # 3. Chargement de la session ou du JSON
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

        # 4. Initialisation par défaut si rien n'existe
        if dico_importance is None and os.path.exists(csv_path):
            liste_eleve_temp = algo.lire_fichier(csv_path)
            dico_importance = algo.init_dico_importance(liste_eleve_temp)
            nb_groupes = 1
            criteres_groupes = []
            
            # Optimisation lecture valeurs
            for nom_crit in liste_crit_brut:
                # On convertit en liste immédiatement pour éviter les problèmes de session
                valeurs_possibles = list(algo.recup_ensemble_val_critere(nom_crit, csv_path))
                criteres_groupes.append({'grp': 1, 'nom': nom_crit, 'valeurs': valeurs_possibles})
            session["valide"] = False

        session["dico_importance"] = dico_importance
        session["criteres_groupes"] = criteres_groupes
        session["nb_groupes"] = nb_groupes
        # Sécurité : on s'assure que nb_groupes est un entier valide
        if not isinstance(nb_groupes, int): nb_groupes = 1
        session["liste_ind_groupes"] = list(range(1, nb_groupes + 1))

        # 5. Gestion du POST (Formulaires)
        if request.method == "POST":
            action = request.form.get("btn")
            
            # Mise à jour des importances
            if dico_importance:
                for crit_nom in dico_importance:
                    crit_propre = crit_nom.lower().replace(" ", "_")
                    nom_input = f"importance_{crit_propre}"
                    valeur = request.form.get(nom_input)
                    if valeur:
                        dico_importance[crit_nom] = int(valeur)
                session["dico_importance"] = dico_importance
            
            # ACTION : VALIDER NOMBRE DE GROUPES
            if action == "btn-valide":
                nb_groupes_str = request.form.get("nb-grp")
                
                # Vérification que l'entrée n'est pas vide
                if nb_groupes_str and nb_groupes_str.strip().isdigit():
                    nb_int = int(nb_groupes_str)
                    session["nb_groupes"] = nb_int
                    session["valide"] = True
                    session["liste_ind_groupes"] = list(range(1, nb_int + 1))
                    
                    tous_les_criteres = []

                    # --- OPTIMISATION ---
                    # On charge les valeurs UNE SEULE FOIS pour ne pas ouvrir le fichier 50 fois
                    cache_valeurs = {}
                    for nom_crit in liste_crit_brut:
                        cache_valeurs[nom_crit] = list(algo.recup_ensemble_val_critere(nom_crit, csv_path))

                    for id_grp in range(1, nb_int + 1):
                        for nom_crit in liste_crit_brut:
                            tous_les_criteres.append({
                                "grp": id_grp,
                                "nom": nom_crit,
                                "valeurs": cache_valeurs[nom_crit]
                            })
                    session["criteres_groupes"] = tous_les_criteres
                else:
                    # Si l'utilisateur n'a rien rentré
                    pass 

            # ACTION : REPARTITION (Checkboxes)
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

        # 6. Préparation pour l'affichage (GET)
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
                # Utilisation de list() pour être sûr que ce soit sérialisable
                dico_valeurs[crit] = list(algo.recup_ensemble_val_critere(crit, csv_path))
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

    except Exception as e:
        # C'est ici que la magie opère : on affiche l'erreur dans le navigateur
        # au lieu de Internal Server Error
        print(f"ERREUR CRITIQUE DANS CONFIGURATION : {e}")
        traceback.print_exc()
        return f"<h1>Une erreur est survenue</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>", 500

@app.route("/repartition/", methods=["POST", "GET"])
def repartition():
    try:
        csv_path = os.path.join(UPLOAD_FOLDER, "groupes.csv")
        dico_importance = session.get("dico_importance", {})
        liste_critere = []

        if request.method == "POST":

            data = request.get_json()

            if data:

                if "dico_importance" in data:
                    session["dico_importance"] = data["dico_importance"]
                    dico_importance = data["dico_importance"]

                if "criteres_groupes" in data:
                    liste_critere = []
                    for critere_data in data["criteres_groupes"]:
                        nouveau_critere = algo.critere.Critere(
                            critere_data["groupe"], critere_data["valeurs"],
                            critere_data["nom_critere"])
                        liste_critere.append(nouveau_critere)
        else:

            liste_critere = []
            for critere in session["criteres_groupes"]:
                liste_critere.append(
                    algo.critere.Critere(critere["grp"], critere["valeurs"],
                                         critere["nom"]))
            liste_eleve_temp = algo.lire_fichier(csv_path)
            if not dico_importance:
                dico_importance = algo.init_dico_importance(liste_eleve_temp)
                session["dico_importance"] = dico_importance

        liste_eleve = algo.lire_fichier(csv_path)
        nombre_groupes = session.get("nb_groupes", 0)

        nb_eleve_groupe = algo.nb_max_eleve_par_groupe(liste_eleve, nombre_groupes)
        liste_nom_critere = algo.recup_critere(csv_path)

        liste_criteres_valeur = []
        for critere in liste_nom_critere:
            liste_valeur_critere = algo.recup_ensemble_val_critere(critere, csv_path)
            liste_criteres_valeur.append(liste_valeur_critere)

        groupes = algo.creer_groupe(liste_eleve, liste_critere, dico_importance, nombre_groupes)
        score = algo.score_totale(liste_eleve, groupes, dico_importance)

        place = str(len(liste_eleve) - len(groupes[-1])) + "/" + str(
            len(liste_eleve))
        try:
            prc_place = str(
                (len(liste_eleve) - len(groupes[-1])) / len(liste_eleve) * 100)
        except ZeroDivisionError:
            prc_place = "0"
        bleu = len(liste_eleve) - len(groupes[-1]) == len(liste_eleve)

        return render_template("repartition.html",
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
                               bleu=bleu)

    except Exception as e:
        print(f"Erreur dans repartition: {e}")
        traceback.print_exc()
        return render_template("repartition.html",
                               error="Une erreur est survenue")


    
@app.route("/exporter_groupes", methods=["POST"])
def exporter_groupes():
    data = request.get_json()
    if not data:
        return "Aucune donnée reçue", 400
    noms_criteres = data.get('noms_criteres', [])
    liste_eleves = data.get('eleves', [])
    csv_path = os.path.join(UPLOAD_FOLDER, "groupes_finaux.csv")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        header = ["Num", "Nom", "Prénom"] + noms_criteres + ["Groupe"]
        writer.writerow(header)
        for eleve in liste_eleves:
            ligne = []
            ligne.append(eleve.get("num"))
            ligne.append(eleve.get("nom"))
            ligne.append(eleve.get("prenom"))
            for val in eleve.get("criteres", []):
                ligne.append(val)
            
            nb_criteres_attendus = len(noms_criteres)
            nb_criteres_recus = len(eleve.get("criteres", []))
            if nb_criteres_recus < nb_criteres_attendus:
                 ligne.extend([""] * (nb_criteres_attendus - nb_criteres_recus))

            ligne.append(eleve.get("groupe"))
            
            writer.writerow(ligne)

    return send_file(csv_path,mimetype="text/csv",as_attachment=True,download_name="liste_groupes.csv",)


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
        print(f"Erreur Export Config: {e}")
        return "Erreur lors de la création du fichier de configuration", 500



@app.route("/api/calculer_stats", methods=["POST"])
def api_calculer_stats():

    try:
        data = request.get_json()


        groupes_data = data.get("groupes", [])
        dico_importance = data.get("dico_importance", {})


        class MockEleve:

            def __init__(self, criteres):
                self.critere = criteres

        liste_eleve_complete = []
        groupes_reconstruits = []

        for grp_idx, liste_eleves_json in enumerate(groupes_data):
            groupe_courant = []
            for el_json in liste_eleves_json:
                nouvel_eleve = MockEleve(el_json.get('criteres', {}))
                groupe_courant.append(nouvel_eleve)
                liste_eleve_complete.append(nouvel_eleve)

            groupes_reconstruits.append(groupe_courant)


        nb_total = len(liste_eleve_complete)
        nb_restants = len(
            groupes_reconstruits[-1]) if groupes_reconstruits else 0
        nb_places = nb_total - nb_restants

        score = algo.score_totale(liste_eleve_complete, groupes_reconstruits,
                                  dico_importance)

        ratio_place = 0
        if nb_total > 0:
            ratio_place = (nb_places / nb_total) * 100

        is_complete = (nb_restants == 0)

        return jsonify({
            "success": True,
            "score": score,
            "place_text": f"{nb_places}/{nb_total}",
            "prc_place": ratio_place,
            "is_complete": is_complete
        })

    except Exception as e:
        print(f"Erreur API Stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
