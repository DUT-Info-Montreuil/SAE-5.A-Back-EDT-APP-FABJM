def get_ressource_statement(row):
    return {
        'idressource': row[0],
        'titre': row[1],
        'nbrheuresemestre': row[2],
        'codecouleur': row[3],
        'idsemestre': row[4]
    }