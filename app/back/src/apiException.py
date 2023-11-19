# -*- coding: utf-8 -*-
# apiException.py

class AucuneDonneeTrouverException(Exception): # get
    """Lever si aucune donnée n'a été trouvé dans la table spécifié
    
    :param table: nom de la table spécifié
    :type table: String
	"""
    def __init__(self, table):
        self.message = f"Aucune donnee dans la table {table} n'a été trouver"
        super().__init__(self.message)

class DonneeIntrouvableException(Exception): # get(id)
    """Lever si aucune donnée correspondant aux critère n'a été trouvé  dans la table spécifié

    :param table: nom de la table spécifié
    :type table: String
    :param id: l'id recherché
    :type id: String
    """
    def __init__(self, table, id):
        self.message = f" Aucune donnée avec l'ID {id} n'a pu être trouvé dans la table {table} "
        super().__init__(self.message)
        
class InsertionImpossibleException(Exception): # post(...)
    """Lever si une erreur est survenue durant l'insertion
    
    :param table: nom de la table spécifié
    :type table: String
	"""
    def __init__(self, table):
        self.message = f" La donnée n'a pas pu être inséré dans la table {table}"
        super().__init__(self.message)
        
class ParamètreTypeInvalideException(Exception): 
    """Lever si un type d'un paramètre ne correspond pas à celui attendue
    
    :param table: nom de la table spécifié
    :type table: String
    
    :param id: l'id recherché
    :type id: String
	"""
    def __init__(self, paramètre, type_valide):
        self.message = f" Le paramètre {paramètre} doit être de type {type_valide} "
        super().__init__(self.message)
        
        