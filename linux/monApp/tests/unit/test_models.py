import pytest
from monApp.static.util.eleve import Eleve
from monApp.static.util.critere import Critere

def test_eleve_init():
    details = {"Genre": "M"}
    eleve = Eleve(1, "Nom", "Prenom", details)
    
    assert eleve.num == 1
    assert eleve.nom == "Nom"
    assert eleve.prenom == "Prenom"
    assert eleve.critere == details

def test_eleve_str_repr():
    details = {"Genre": "F"}
    eleve = Eleve(2, "Nom2", "Prenom2", details)
    attendu = "2 Nom2 Prenom2 {'Genre': 'F'}"
    
    assert str(eleve) == attendu
    assert repr(eleve) == attendu

def test_critere_init():
    critere = Critere(1, ["1", "2", "3", "4", "5", "6", "7"], "Niveau Maths")
    
    assert critere.groupe == 1
    assert critere.condition == ["1", "2", "3", "4", "5", "6", "7"]
    assert critere.nom_critere == "Niveau Maths"

def test_critere_str_repr():
    critere = Critere(2, ["A", "B", "C"], "Pénibilité")
    attendu = "2 ['A', 'B', 'C'] Pénibilité"
    
    assert str(critere) == attendu
    assert repr(critere) == attendu