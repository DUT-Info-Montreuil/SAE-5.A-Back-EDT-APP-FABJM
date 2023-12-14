def get_cours_statement(row):
    """ 
    Fonction de mappage de la table cours
    
    :param row: donnée représentant un cours
    :type row: tableau
    
    :return: les données représentant un cours
    :rtype: dictionnaire
    """
    return {
        'idCours':row[0],
        'HeureDebut':str(row[1]),
        'NombreHeure':row[2],
        'Jour':row[3],
        'idRessource':row[4]
    }