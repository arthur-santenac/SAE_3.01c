class Critere():
    """ Classe représentant un critère d'un groupe
    """

    def __init__(self, groupe, condition):
        self.groupe = groupe
        self.condition = condition

    def __str__(self):
        return f"{self.groupe} {self.condition}"