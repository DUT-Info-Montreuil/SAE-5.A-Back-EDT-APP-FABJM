# -*- coding: utf-8 -*-
# apiException.py

class AucuneDonneeTrouverException(Exception): 
    """Lever si aucune donnée n'a été trouvé dans la table spécifié
    
    :param table: nom de la table spécifié
    :type table: String
	"""
    def __init__(self, table):
        self.message = f"Aucune donnee dans la table {table} n'a été trouver"
        super().__init__(self.message)

class DonneeIntrouvableException(Exception): 
    """Lever si aucune donnée correspondant aux critère n'a été trouvé  dans la table spécifié

    :param table: nom de la table spécifié
    :type table: String
    :param id: l'id recherché
    :type id: String
    """
    def __init__(self, table, id = -1):
        if id != -1:
            self.message = f" Aucune donnée avec l'ID {id} n'a pu être trouvé dans la table {table} "
        else:
            self.message = f" Aucune donnée répondant aux critères n'a pu être trouvé dans la table {table} "
        super().__init__(self.message)
        
class ActionImpossibleException(Exception): 
    """Lever si une erreur est survenue durant l'insertion
    
    :param table: nom de la table spécifié
    :type table: String
	"""
    def __init__(self, table, action = "inséré"):
        self.message = f" La donnée n'a pas pu être {action} dans la table {table}"
        super().__init__(self.message)

class DonneeExistanteException(Exception): 
    """Lever si une donnée existe déjà sur une clé unique
    
    :param table: nom de la table spécifié
    :type table: String
    :param column: nom de la colonne spécifié
    :type column: String
    :param value: valeur de la colonne spécifié
    :type value: String
    """
    def __init__(self, value, column, table):
        self.message = f" La donnée {value} existe déjà dans la colonne {column} de la table {table} "
        super().__init__(self.message)
        
        
class ParamètreTypeInvalideException(Exception): 
    """Lever si un type d'un paramètre ne correspond pas à celui attendue
    
    :param paramètre: le nom du paramètre spécifié
    :type paramètre: String
    
    :param type_valide: le type valide
    :type type_valide: String
	"""
    def __init__(self, paramètre, type_valide):
        self.message = f" Le paramètre {paramètre} doit être de type {type_valide} "
        super().__init__(self.message)

class ParamètreInvalideException(Exception): 
    """Lever si un paramètre est invalide
    
    :param paramètre: le nom du paramètre spécifié
    :type paramètre: String

    :param message: message d'erreur personnalisé qui vas écraser celui par défaut
    :type message: String(optionnel)
	"""
    def __init__(self, paramètre, message = None):
        if message != None:
            self.message = message
        else:
            self.message = f" La valeur spécifié pour le paramètre {paramètre} est invalide"
        super().__init__(self.message)
        
class LoginOuMotDePasseInvalideException(Exception): 
    """Lever si le login ou le mot de passe est invalide

    """
    def __init__(self):
        self.message = f" Le login ou le mot de passe est invalide "
        super().__init__(self.message)

class ParamètreBodyManquantException(Exception): 
    """Lever si Au moins un paramètre d'entrée attendue dans le body est manquant
    
    :param paramètre: le nom du paramètre manquant, None par défaut
    :type paramètre: String
	"""
    def __init__(self, parametre = None):
        if parametre != None:
            self.message = f"Le paramètre d'entrée {parametre} attendue dans le body est manquant"
        else:
            self.message = f"Au moins un paramètre d'entrée attendue dans le body est manquant"
        super().__init__(self.message)

class PermissionManquanteException(Exception): 
    """Lever si l'utilisateur n'a pas assez de droit pour effectuer une action
    
	"""
    def __init__(self):
        self.message = f"Vous ne possédez pas d'assez de permission pour effectuer cette action"
        super().__init__(self.message)

class AuthentificationFailedException(Exception): 
    """Lever si l'authentification a échoué
    
	"""
    def __init__(self):
        self.message = f"L'authentification a échoué, accès refusé"
        super().__init__(self.message)