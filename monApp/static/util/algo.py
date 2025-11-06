import time
import csv
import eleve
import critere
import random
import copy
import json

def lire_fichier(nom_fichier):
    """ Lit un fichier csv et le transforme en liste

    Args:
        nom_fichier (str): nom d'un fichier csv

    Returns:
        list: liste contenant les informations des élèves
    """
    liste_eleve = []
    with open(nom_fichier) as fichier_csv:
        reader = csv.reader(fichier_csv, delimiter=',')
        criteres = next(reader)[3:]
        for ligne in reader:
            dico_critere = dict()
            liste_critere = ligne[3:]
            for i in range(len(liste_critere)):
                dico_critere[criteres[i]] = liste_critere[i]
            new_eleve = eleve.Eleve(ligne[0], ligne[1], ligne[2], dico_critere)
            liste_eleve.append(new_eleve)
    return liste_eleve

def exporter_fichier():
    ...

def lire_config(nom_fichier):
    with open(nom_fichier) as fichier_json:
        config = json.load(fichier_json)
    liste_critere = []
    for un_critere in config["liste_critere"]:
        liste_critere.append(critere.Critere(un_critere["groupe"], un_critere["appartient"], un_critere["nom"]))
    dico_importance = config["dico_importance"]
    return liste_critere, dico_importance

def exporter_config(liste_critere, dico_importance):
    ...

def init_dico_importance(liste_eleve):
    dico_importance = {}
    if len(liste_eleve) > 0:
        for critere in liste_eleve[0].critere:
            dico_importance[critere] = 100 // len(liste_eleve[0].critere)
    return dico_importance

def cout(variable1, variable2):
    """Calcule le cout entre deux instances d'une variable en faisant la valeur absolue des différences des valeurs des variables

    Args:
        variable1 (dict): dictionnaire de valeurs d'une variable. Les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        variable2 (dict): dictionnaire de valeurs d'une variable. Les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        coefficient (int) : coefficient d'importance de la variable

    Returns:
        int : différence des deux variables. Plus ce cout est élevé plus les valeurs des variables sont différentes
    """
    cout = 0
    for elem in variable2:
        cout += abs(variable2[elem] - variable1[elem])
    return cout

def diff_cout_groupe(groupe1, groupe2, dico_importance):
    """calcule et renvoie le cout entre deux groupes. 

    Args:
        groupe1 (dict): clé : le nom d'un crière valeur : des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        groupe2 (dict): clé : le nom d'un crière valeur : des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        dico_importance (dict) : Dictionnaire avec comme clés les noms de variables et commes valeurs les coefficients d'importance.

    Returns:
        int : cout pour les deux groupes. Plus ce cout est élevé plus les valeurs des variables sont différentes
    """
    cout_res = 0
    if len(groupe1) == len(groupe2):
        for critere in groupe1:
            cout_res += dico_importance[critere] * cout(groupe1[critere], groupe2[critere])
    return cout_res

def cout_tot(groupe, liste_groupes, dico_importance):
    """calcule et renvoie le cout entre un groupe et une liste de groupes. 
    Args:
        group (list): Ce premier groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        liste_group (list): liste de groupes
        dico_importance (dict) : Dictionnaire avec comme clés les noms de variables et commes valeurs les coefficients d'importance.
    
    Returns:
        int : cout entre le groupe "group" et la liste de groupes
    """
    cout_total = 0
    for un_groupe in liste_groupes:
        pourcentage = dico_poucentage(un_groupe)
        cout_total += diff_cout_groupe(groupe, pourcentage, dico_importance)
    return cout_total

def nb_max_eleve_par_groupe(liste_eleve, nb_groupes):
    """Retourne le nombre de personne maximum par groupes

    Args:
        liste_eleve (list): la liste des élèves
        nb_groupes (int): nombre de groupes souhaités

    Returns:
        int: le nombre d'élèves maximum par jour
    """
    if len(liste_eleve) % nb_groupes == 0 :
        return len(liste_eleve) // nb_groupes
    else:
        return len(liste_eleve) // nb_groupes + 1

def groupes_possible(liste_groupes, liste_eleve, eleve, liste_critere, nb_groupes):
    """Renvoie une liste d'index qui sont les index des groupes dans lesquels on peut ajouter des élèves.

    Args:
        liste_groupes (list): une liste de listes qui represente la liste de groupes.
        nb_elv_grp (int): nombre d'eleve max par grp

    Returns:
        list: Une liste d'index.
    """
    nb_elv_grp = nb_max_eleve_par_groupe(liste_eleve, nb_groupes)
    res = []
    for i in range(len(liste_groupes) - 1):
        ajouter = True
        if len(liste_groupes[i]) >= nb_elv_grp:
            ajouter = False
        for critere in liste_critere:
            if critere.groupe == i + 1:
                if int(eleve.critere[critere.nom_critere]) not in critere.condition:
                    ajouter = False
        if ajouter:
            res.append(i)
    return res

def dico_poucentage(liste_eleves):
    """Permet d'avoir une liste de dictionnaires avec pour chaque valeur de chaque catégorie le pourcentage par rapport au total de la catégorie

    Args:
        liste_eleve (list): la liste des élèves

    Returns:
        liste(dictionnaire): Une liste de dictionnaires où chaque dictionnaire correspond à une colonne. Chaque dictionnaire contient les valeurs uniques
                            de la colonne comme clés et leur pourcentage d'apparition comme valeurs.
    """
    diviseur = len(liste_eleves)
    dico_res = {}
    if len(liste_eleves) > 0:
        for critere in liste_eleves[0].critere.keys():
            dico_total = {}
            for eleve in liste_eleves:
                valeur_critere = eleve.critere[critere]
                if valeur_critere not in dico_total:
                    dico_total[valeur_critere] = 1
                else:
                    dico_total[valeur_critere] += 1
            for cle, valeur in dico_total.items():
                dico_total[cle] = (valeur / diviseur) * 100
            dico_res[critere] = dico_total
    return dico_res

def max_aleatoire(liste_cout):
    """ Renvoie l'indice de l'élément le plus petit de la liste,
        si il y en a plusieurs renvoie un indice aléatoire parmis ceux des élément les plus petits

    Args:
        liste_cout (list): liste de cout d'insertion d'un élève dans un groupe

    Returns:
        int: indice pour insérer un élève
    """
    max_val = max(liste_cout)
    liste_index = []
    for i in range(len(liste_cout)):
        if liste_cout[i] == max_val:
            liste_index.append(i)
    return random.choice(liste_index)

def creer_groupe(liste_eleve, liste_critere, dico_importance, nb_groupe):
    """ creer des groupes d'élève en répartissant les critères

    Args: 
        liste_eleve (list): liste des élèves importer d'un fichier csv
        dico_importance (dict): dictionnaire contenant les coefficient d'importance des critères
        nb_groupe (int): nombre de groupes a créer

    Returns:
        list: liste des groupes finis
    """
    liste_max = None
    debut, actuel = time.time(), time.time()
    dico_pourc_elv = dico_poucentage(liste_eleve)
    cpt = 0
    while actuel - debut < 3:
        cpt += 1
        actuel = time.time()
        random.shuffle(liste_eleve)
        liste_groupes = []
        for _ in range(nb_groupe + 1):
            liste_groupes.append([])
        for eleve in liste_eleve:
            liste_groupes_possibles = groupes_possible(liste_groupes, liste_eleve, eleve, liste_critere, nb_groupe)
            if len(liste_groupes_possibles) > 0:
                liste_cout = []
                for ind_groupe in liste_groupes_possibles:
                    if len(liste_groupes[ind_groupe]) == 0:
                        liste_cout.append(float('inf'))
                    else:
                        groupe_simul = copy.deepcopy(liste_groupes[ind_groupe])
                        ancien_cout = diff_cout_groupe(dico_pourc_elv, dico_poucentage(groupe_simul), dico_importance)
                        groupe_simul.append(eleve)
                        nouveau_cout = diff_cout_groupe(dico_pourc_elv, dico_poucentage(groupe_simul), dico_importance)
                        liste_cout.append(ancien_cout - nouveau_cout)
                liste_groupes[liste_groupes_possibles[max_aleatoire(liste_cout)]].append(eleve)
            else:
                liste_groupes[-1].append(eleve)
        if liste_max is None or len(liste_groupes[-1]) < len(liste_max[-1]) or cout_tot(dico_pourc_elv, liste_groupes, dico_importance) < cout_tot(dico_pourc_elv, liste_max, dico_importance):
            liste_max = copy.deepcopy(liste_groupes)
    print(cpt)
    return liste_max

def score_totale(liste_eleve, groupes, dico_importance):
    dico_pourc_elv = dico_poucentage(liste_eleve)
    cout_grp = cout_tot(dico_pourc_elv, groupes, dico_importance)
    cout_totale = 0
    for critere in dico_pourc_elv:
        cout_totale += 100 * dico_importance[critere] * (len(groupes) - 1)
    return int((cout_totale - cout_grp) / cout_totale * 100) 

liste_eleve = lire_fichier("monApp/static/exemple/eleves.csv")

dico_importance = init_dico_importance(liste_eleve)

print(dico_importance)

# liste_critere, dico_importance = [], {"genre" : 1, "niveau Français" : 0}
# liste_critere, dico_importance = lire_config("monApp/static/exemple/config.json")
# liste_critere = [critere.Critere(2, [4, 5, 6], "niveau Maths"), critere.Critere(2, [5, 6], "niveau Français"), critere.Critere(3, [4, 5, 6], "niveau Maths")]
# dico_importance = {"genre" : 3, "niveau Français" : 0, "niveau Maths" : 0, "Pénibilité" : 3}

# groupes = creer_groupe(liste_eleve, liste_critere, dico_importance, 12)
# score = score_totale(liste_eleve, groupes, dico_importance)

# nb_eleve_groupe=[]
# for groupe in groupes:
#     nb_eleve_groupe.append(len(groupe))
#     for elev in groupe:
#         print(elev)
#     print()

# print(f"Score : {score}%")

