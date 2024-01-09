def get_equipement_statement(row):
    """ 
    Fonction de mappage de la table equipement
    
    :param row: donnée représentant un equipement
    :type row: tableau
    
    :return: les données représentant un equipement
    :rtype: dictionnaire
    """
    return {
        'idEquipement':row[0],
        'Nom':row[1]
    }