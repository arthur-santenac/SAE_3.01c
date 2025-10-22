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

def cout(variable1, variable2, coefficient):
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
    if len(variable1) == len(variable2):
        for elem in variable1:
            cout += abs(variable2[elem] - variable1[elem]) * coefficient
    return cout

def diff_cout_groupe(groupe1, groupe2, dico_importance):
    """calcule et renvoie le cout entre deux groupes. 

    Args:
        groupe1 (list): Ce premier groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        groupe2 (list): Ce deuxième groupe est une liste de variables. Les variables sont des dictionnaires où les clés sont les différentes valeurs trouvées 
        dans le fichier csv et les valeurs associées sont le pourcentage d'élèves associés à cette valeur dans le groupe de la variable.
        dico_importance (dict) : Dictionnaire avec comme clés les noms de variables et commes valeurs les coefficients d'importance.

    Returns:
        int : cout pour les deux groupes. Plus ce cout est élevé plus les valeurs des variables sont différentes
    """    
    cout_res = 0
    if len(groupe1) == len(groupe2):
        for i in range(len(groupe1)):
            cout_res += cout(groupe1[i], groupe2[i], dico_importance.values()[i])
    return cout_res

def cout_tot(group, liste_groupes, dico_importance):
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
    for groupe in liste_groupes:
        cout_total += diff_cout_groupe(group, groupe, dico_importance)
    return cout_total

