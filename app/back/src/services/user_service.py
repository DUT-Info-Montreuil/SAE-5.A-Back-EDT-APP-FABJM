def get_utilisateur_statement(row):
    """ 
    Fonction de mappage de la table utilisateur
    
    :param row: donnée représentant un utilisateur
    :type row: tableau
    
    :return: les données représentant un utilisateur
    :rtype: dictionnaire
    """
    return {
        'IdUtilisateur':row[0],
        'FirstName':row[1],
        'LastName':row[2],
        'Username':row[3],
        'PassWord':row[4],
        'FirstLogin':row[5]
    }

def get_professeur_statement(row):
    """ 
    Fonction de mappage de la table professeur
    
    :param row: donnée représentant un professeur
    :type row: tableau
    
    :return: les données représentant un professeur
    :rtype: dictionnaire
    """
    return {
        'idProf':row[0],
        'Initiale':row[1],
        'idSalle':row[2],
        'idUtilisateur':row[3]
    }

def get_professeur_statement_extended(row):
    """ 
    Fonction de mappage de la table professeur contenant des données de la table utilisateur
    
    :param row: donnée représentant un professeur
    :type row: tableau
    
    :return: les données représentant un professeur
    :rtype: dictionnaire
    """
    return {
        'idProf':row[0],
        'Initiale':row[1],
        'idSalle':row[2],
        'FirstName':row[3],
        'LastName':row[4],
        'idUtilisateur':row[5]
    }

def get_manager_statement(row):
    """ 
    Fonction de mappage de la table manager
    
    :param row: donnée représentant un manager
    :type row: tableau
    
    :return: les données représentant un manager
    :rtype: dictionnaire
    """
    return {
        'idManager':row[0],
        'idProf':row[1],
        'idGroupe':row[2]
    }









    
