def get_semestre_statement(row):
    """ 
    Fonction de mappage de la table semestre
    
    :param row: donnée représentant un semestre
    :type row: tableau
    
    :return: les données représentant un semestre
    :rtype: dictionnaire
    """
    return {
        'IdSemestre': row[0],
        'Numero': row[1]
    }
