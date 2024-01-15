def get_salle_statement(row):
    """ 
    Fonction de mappage de la table salle
    
    :param row: donnée représentant un salle
    :type row: tableau
    
    :return: les données représentant un salle
    :rtype: dictionnaire
    """
    return {
        'idSalle':row[0],
        'Nom':row[1],
        'Capacite':row[2]
    }