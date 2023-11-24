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
    








    
