import src.connect_pg as connect_pg

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
        'Jour':str(row[3]),
        'idRessource':row[4]
    }

def getCoursProf(idUtilisateur , conn):
    """ Renvoie les cours au quelle enseigne un professeur
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les cours
    :rtype: list
    """
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    result = connect_pg.get_query(conn , f"Select edt.cours.* from edt.cours inner join edt.enseigner as e1 using(idCours)  where e1.idProf = {idProf} order by idCours asc")
    
    return result

def getCoursGroupeService(idGroupe , conn):
    """ Renvoie les cours d'un groupe 
    
    :param idGroupe: idGroupe d'un groupe
    :type idGroupe: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: les cours
    :rtype: list
    """
    result = connect_pg.get_query(conn , f"Select edt.cours.* from edt.cours inner join edt.etudier  using(idCours)  inner join edt.groupe as e1 using (idGroupe) where e1.idGroupe = {idGroupe} order by idCours asc")
    
    return result

    