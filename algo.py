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



def csv_en_liste_de_liste(nom_fichier):
    """
    Ouvre un fichier CSV et renvoie son contenu sous forme d'une liste de listes.
    """
    contenu = []


    with open(nom_fichier, "r") as fichier:
        lecteur = csv.reader(fichier)
        for ligne in lecteur:
            contenu.append(ligne) 
    return contenu 

def equilibre_genre(list_eleves):
    """donne l'objectif du nombre de filles et de garçons par groupe si on veut une mixité

    Args:
        list_eleves (list): liste des élèves pour les groupes
        nb_groupe (int): nombre de groupes souhaités

    Returns:
        tuple: tuple de deux nombres. Le premier est l'objectif de garçon, le deuxième est l'objectif de filles. Les deux sont en pourcentage
    """    
    total_genre = [0, 0]
    for eleve in list_eleves:
        genre = eleve.critere["genre"]
        if genre == "M":
            total_genre[0] += 1
        elif genre == "F":
            total_genre[1] += 1
    pct_G = (total_genre[0] / (total_genre[0]+total_genre[1])) * 100
    pct_F = (total_genre[1] / (total_genre[0]+total_genre[1])) * 100
    res_pourcentage = (pct_G, pct_F)
    print("il faut essayer d'avoir au moins " + str(res_pourcentage[0]) +"% garçons par groupe et " + str(res_pourcentage[1]) +"% filles par groupe pour avoir")
    print("une mixité maximale.")
    return res_pourcentage

equilibre_genre(lire_fichier("exemple.csv"))


def equilibre(fichier):
    """Permet d'avoir une liste de dictionnaires avec pour chaque valeur de chaque catégorie le pourcentage par rapport au total de la catégorie

    Args:
        fichier (liste(liste)): une liste de liste qui represente le fichier .csv

    Returns:
        liste(dictionnaire): Une liste de dictionnaires où chaque dictionnaire correspond à une colonne. Chaque dictionnaire contient les valeurs uniques
                            de la colonne comme clés et leur pourcentage d'apparition comme valeurs.
    """
    liste=[]
    diviseur=len(fichier)-1
    for colone in range(3,len(fichier[0])):
        dico_total={}
        for ligne in fichier[1:]:
            if ligne[colone] not in dico_total:
                dico_total[ligne[colone]]=1
            else:
                dico_total[ligne[colone]]+=1

        for cle,valeur in dico_total.items():
            dico_total[cle]=(valeur/diviseur)*100
        
        liste.append(dico_total)

    return liste







    


#     for _ in range(3,len())

print(equilibre(csv_en_liste_de_liste("exemple.csv")))

