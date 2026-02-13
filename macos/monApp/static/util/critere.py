class Critere():
    """ Classe représentant un critère d'un groupe
    """

    def __init__(self, groupe :int, condition :list[str], nom_critere: str):
        self.groupe = groupe
        self.condition = condition
        self.nom_critere = nom_critere

    def __str__(self):
        return f"{self.groupe} {self.condition} {self.nom_critere}"
    
    def __repr__(self):
        return str(self)
