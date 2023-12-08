def get_groupe_statement(row):
    """
    Fonction de mappage de la table utilisateur

    :param row: donnée représentant un utilisateur
    :type row: tableau

    :return: les données représentant un utilisateur
    :rtype: dictionnaire
    """
    return {
        'IdGroupe': row[0],
        'Nom': row[1],
        'AnneeScolaire': row[2],
        'Annee': row[3],
        'idGroupe_1': row[4],
    }
