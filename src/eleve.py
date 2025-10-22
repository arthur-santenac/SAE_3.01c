class Eleve():
    """ Classe représentant un élève du collège
    """

    def __init__(self, num=int, nom=str, prenom=str, critere=dict):
        self.num = num
        self.nom = nom
        self.prenom = prenom
        self.critere = critere

    def __str__(self):
        return f"{str(self.num)} {self.nom} {self.prenom} {self.critere}"
    
    def __repr__(self):
        return str(self.num)+" "+self.nom