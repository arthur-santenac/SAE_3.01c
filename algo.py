import csv
import eleve

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

liste_eleve = lire_fichier("exemple.csv")
liste_critere = []

def equilibre_genre(list_eleves, nb_groupe):
    """donne l'objectif du nombre de filles et de garçons par groupe si on veut une mixité

    Args:
        list_eleves (list): liste des élèves pour les groupes
        nb_groupe (int): nombre de groupes souhaités

    Returns:
        tuple: tuple de deux nombres. Le premier est l'objectif de garçon, le deuxième est l'objectif de filles
    """    
    total_genre = [0, 0]
    for eleve in list_eleves:
        genre = eleve.critere["genre"]
        if genre == "M":
            total_genre[0] += 1
        elif genre == "F":
            total_genre[1] += 1
    res = (total_genre[0]//nb_groupe, total_genre[1]//nb_groupe)
    print("il faut essayer d'avoir au moins " + str(res[0]) +" garçons par groupe et " + str(res[1]) +" filles par groupe pour avoir")
    print("une mixité maximum dans les " + str(nb_groupe) + " groupes")
    return res
