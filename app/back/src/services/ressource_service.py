def get_ressource_statement(row):
    return {
        'idressource': row[0],
        'titre': row[1],
        'numero' : row[2],
        'nbrheuresemestre': row[3],
        'codecouleur': row[4],
        'idsemestre': row[5]
    }