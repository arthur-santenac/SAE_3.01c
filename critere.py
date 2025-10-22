class Critere():
    """ Classe représentant un critère d'un groupe
    """

    def __init__(self, groupe, condition, nom_critere, obligatoire):
        self.groupe = groupe
        self.condition = condition
        self.nom_critere = nom_critere
        self.obligatoire = obligatoire

    def __str__(self):
        return f"{self.groupe} {self.condition} {self.nom_critere} {self.obligatoire}"
    
    def __repr__(self):
        return str(self)