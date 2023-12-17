def get_ressource_statement(row):
    """ 
    Fonction de mappage de la table ressource
    
    :param row: donnée représentant un ressource
    :type row: tableau
    
    :return: les données représentant un ressource
    :rtype: dictionnaire
    """
    return {
        'idressource': row[0],
        'titre': row[1],
        'numero' : row[2],
        'nbrheuresemestre': row[3],
        'codecouleur': row[4],
        'idsemestre': row[5]
    }