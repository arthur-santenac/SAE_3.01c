from monApp.static.util import algo
from monApp.static.util.eleve import Eleve
from monApp.static.util.critere import Critere

def test_lire_fichier():
    nom_fichier = 'monApp/static/exemple/exemple2.csv'
    liste_eleves = algo.lire_fichier(nom_fichier)
    assert isinstance(liste_eleves, list)
    assert len(liste_eleves) == 24
    assert all(isinstance(e, Eleve) for e in liste_eleves)
    premier = liste_eleves[0]
    assert premier.num == '1'
    assert premier.nom == 'nom1'
    assert premier.prenom == 'prenom1'
    assert isinstance(premier.critere, dict)
    assert premier.critere['genre'] == 'M'
    assert premier.critere['niveau Français'] == '1'

def test_recup_critere():
    nom_fichier = 'monApp/static/exemple/exemple2.csv'
    liste_criteres = algo.recup_critere(nom_fichier)
    assert liste_criteres[0] == "genre"
    assert liste_criteres[1] == "niveau Français"
    
    nom_fichier = 'monApp/static/exemple/exemple.csv'
    liste_criteres2 = algo.recup_critere(nom_fichier)
    assert liste_criteres2[0] == "genre"
    assert liste_criteres2[1] == "niveau Français"
    assert not liste_criteres2[2] == "Pénibilité"
    assert liste_criteres2[3] == "Pénibilité"
    

def test_init_dico_importance():
    eleve_test = Eleve("1", "Test", "Test", {"Niveau Maths": "4", "Niveau Francais": "4", "Pénibilité": "B", "Test" : "B"})
    liste_eleve = [eleve_test]
    dico_imp = algo.init_dico_importance(liste_eleve)
    assert len(dico_imp) == 4
    assert dico_imp["Niveau Maths"] == 25

def test_cout():
    g1 = {'1': 50.0, '2': 50.0}
    g2 = {'1': 50.0, '2': 50.0}
    assert algo.cout(g1, g2) == 0
    g3 = {'1': 100.0, '2': 0.0}
    g4 = {'1': 0.0, '2': 100.0}
    assert algo.cout(g3, g4) == 200

def test_diff_cout_groupe():
    g1 = {'Genre': {'M': 50.0, 'F': 50.0}, 'Niveau': {'1': 100.0, '2': 0.0}}
    g2 = {'Genre': {'M': 50.0, 'F': 50.0}, 'Niveau': {'1': 0.0, '2': 100.0}}
    dico_importance = {'Genre': 1, 'Niveau': 2}
    res = algo.diff_cout_groupe(g1, g2, dico_importance)
    assert res == 400

def test_cout_tot():
    ref_groupe = {'Genre': {'M': 50.0, 'F': 50.0}}
    liste_groupes = [[Eleve("1", "A", "A", {'Genre': 'M'}), Eleve("2", "B", "B", {'Genre': 'F'})], [Eleve("3", "C", "C", {'Genre': 'M'}), Eleve("4", "D", "D", {'Genre': 'M'})]]
    dico_importance = {'Genre': 1}
    total = algo.cout_tot(ref_groupe, liste_groupes, dico_importance)
    assert total == 50.0

def test_nb_max_eleve_par_groupe():
    liste_10 = [1] * 10
    assert algo.nb_max_eleve_par_groupe(liste_10, 2) == 5
    assert algo.nb_max_eleve_par_groupe(liste_10, 3) == 4

def test_groupes_possible():
    liste_eleve = [0] * 10 
    grp0 = []
    grp1 = []
    grp2 = []
    grp3 = []
    liste_groupes = [grp0, grp1, grp2, grp3]
    eleve = Eleve("1", "TEST", "TEST", {"Genre": "F", "Niveau Français": "2"})
    critere1 = Critere(1, ["1"], "Niveau Français")
    critere2 = Critere(2, ["1", "2"], "Niveau Français")
    critere3 = Critere(3, ["1", "2"], "Niveau Français")
    res = algo.groupes_possible(liste_groupes, liste_eleve, eleve, [critere1, critere2, critere3], 3)
    assert 0 not in res
    assert 1 in res
    assert 2 in res

def test_dico_poucentage():
    e1 = Eleve("1", "nom1", "prenom1", {"Genre": "M"})
    e2 = Eleve("2", "nom2", "prenom2", {"Genre": "F"})
    e3 = Eleve("3", "nom3", "prenom3", {"Genre": "M"})
    e4 = Eleve("4", "nom4", "prenom4", {"Genre": "M"})
    dico = algo.dico_poucentage([e1, e2, e3, e4])
    assert dico["Genre"]["M"] == 75.0
    assert dico["Genre"]["F"] == 25.0

def test_max_aleatoire():
    liste1 = [10, 50, 20]
    assert algo.max_aleatoire(liste1) == 1
    liste2 = [10, 50, 50, 20]
    res = algo.max_aleatoire(liste2)
    assert res in [1, 2]

def test_creer_groupe():

    e1 = Eleve("1", "e1", "test", {"Genre": "M"})
    e2 = Eleve("2", "e2", "test", {"Genre": "F"})
    e3 = Eleve("3", "e3", "test", {"Genre": "F"})
    eleves = [e1, e2, e3]
    dico_importance = {"Genre": 1}
    liste_critere = []
    nb_groupe = 3
    groupes = algo.creer_groupe(eleves, liste_critere, dico_importance, nb_groupe)
    assert len(groupes) == nb_groupe + 1
    assert len(groupes[0]) == len(groupes[1]) == len(groupes[2]) 
    assert groupes[3] == []

def test_score_totale():
    e1 = Eleve("1", "e1", "test", {"Genre": "M"})
    e2 = Eleve("2", "e2", "test", {"Genre": "F"})
    e3 = Eleve("3", "e3", "test", {"Genre": "F"})
    e4 = Eleve("4", "e4", "test", {"Genre": "F"})
    groupes = [[e1], [e2], [e3], [e4]]
    groupes2 = [[e1], [e2]]
    dico_imp = {"Genre": 1}
    score = algo.score_totale([e1, e2, e3, e4], groupes, dico_imp)
    score2 = algo.score_totale([e1, e2], groupes2, dico_imp)
    assert score == 50
    assert score2 == 0