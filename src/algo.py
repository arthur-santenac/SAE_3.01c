import csv
import src.eleve as eleve
import src.critere as critere

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
        criteres =  next(reader)[3:]
        for ligne in reader:
            dico_critere = dict()
            liste_critere = ligne[3:]
            for i in range(len(liste_critere)):
                dico_critere[criteres[i]] = liste_critere[i]
            new_eleve = eleve.Eleve(ligne[0], ligne[1], ligne[2], dico_critere)
            liste_eleve.append(new_eleve)
    return liste_eleve

def cout(variable1, variable2):
    """Calcule le cout entre deux instances d'une variable en faisant la valeur absolue des différences des valeurs des variables

    Args:
        variable1 (dict): dictionnaire de valeurs d'une variable. Les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        variable2 (dicr): dictionnaire de valeurs d'une variable. Les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.

    Returns:
        int : différence des deux variables. Plus ce cout est élevé plus les valeurs des variables sont différentes
    """    
    cout = 0
    if len(variable1) == len(variable2):
        for elem in variable1:
            cout += abs(variable2[elem] - variable1[elem])
    return cout

def diff_cout_groupe(groupe1, groupe2):
    """calcule et renvoie le cout entre deux groupes. 

    Args:
        groupe1 (list): Ce premier groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        groupe2 (list): Ce deuxième groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.

    Returns:
        int : cout pour les deux groupes. Plus ce cout est élevé plus les valeurs des variables sont différentes
    """    
    cout_res = 0
    if len(groupe1) == len(groupe2):
        for i in range(len(groupe1)):
            cout_res += cout(groupe1[i], groupe2[i])
    return cout_res

def cout_tot(group, liste_groupes):
    """calcule et renvoie le cout entre un groupe et une liste de groupes. 
    Args:
        group (list): Ce premier groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        liste_group (list): liste de groupes
    """    
    cout_total = 0
    for groupe in liste_groupes:
        cout_total += diff_cout_groupe(group, groupe)
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

def groupes_possible(liste_groupes, nb_elv_grp):
    """Renvoie une liste d'index qui sont les index des groupes dans lesquels on peut ajouter des élèves.

    Args:
        liste_groupes (list): une liste de listes qui represente la liste de groupes.
        nb_elv_grp (int): nombre d'eleve max par grp

    Returns:
        list: Une liste d'index.
    """   
    res = []
    for i in range(len(liste_groupes)):
        if len(liste_groupes[i]) < nb_elv_grp:
            res.append(i)
    return res

def creer_groupe(liste_eleve, dico_importance, nb_groupe):
    liste_groupes = [[]] * nb_groupe
    dico_equil_elv = ...
    nb_elv_grp = nb_max_eleve_par_groupe(liste_eleve, nb_groupe)
    for eleve in liste_eleve:
        liste_groupes_possibles = groupes_possible(liste_groupes, nb_elv_grp)
        liste_cout = []
        for ind_groupe in liste_groupes_possibles:
            liste_simul = []
            for grp in liste_groupes:
                liste_simul.append(...(grp.copy()))
            liste_simul[ind_groupe].append(eleve)
            liste_cout.append(cout_tot(dico_equil_elv, liste_simul))
        liste_groupes_possibles[liste_cout.index(max(liste_cout))].append(eleve)
    return liste_groupes

liste_eleve = lire_fichier("exemple2.csv")
dico_importance = {"genre" : 3, "niveau Français" : 1}
groupes = creer_groupe(liste_eleve, dico_importance, 3)

for groupe in groupes:
    for elev in groupe:
        print(elev)
    print()
liste_eleve = lire_fichier("exemple.csv")
liste_critere = []
