import csv
import eleve
import critere

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

def creer_groupe(liste_eleve, dico_importance, nb_groupe):
    liste_groupes = [[]] * nb_groupe
    dico_equil_elv = ...
    nb_elv_grp = ... 
    for eleve in liste_eleve:
        liste_groupes_possibles = ... # groupes_possibles(liste_groupes, nb_elv_grp)
        liste_cout = []
        for ind_groupe in liste_groupes_possibles:
            liste_simul = []
            for grp in liste_groupes:
                liste_simul.append(grp.copy())
            liste_simul[ind_groupe].append(eleve)            
            liste_cout.append(...)
        liste_groupes_possibles[liste_cout.index(max(liste_cout))].append(eleve)
    return liste_groupes

liste_eleve = lire_fichier("exemple2.csv")
dico_importance = {"genre" : 3, "niveau Français" : 1}
groupes = creer_groupe(liste_eleve, dico_importance, 3)

for groupe in groupes:
    for elev in groupe:
        print(elev)
    print()
