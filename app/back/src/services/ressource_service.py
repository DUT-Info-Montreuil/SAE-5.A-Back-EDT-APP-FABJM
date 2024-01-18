import datetime
import src.connect_pg as connect_pg

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

def getRessourceProf(idUtilisateur , conn):
    """ Renvoie les ressources au quelle enseigne un professeur
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les ressources
    :rtype: list
    """
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    result = connect_pg.get_query(conn , f"SELECT edt.ressource.* from edt.ressource inner join edt.responsable as r1 using(idRessource)  where r1.idProf = {idProf} order by idRessource asc")
    
    return result

def getRessourceEleve(idUtilisateur , conn):
    """ Renvoie les ressources qu'un élève étudie
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les ressources
    :rtype: list
    """
    result = connect_pg.get_query(conn , f"SELECT edt.ressource.* from edt.ressource inner join edt.cours using(idRessource) inner join edt.etudier using(idCours) inner join edt.eleve as e1 using(idGroupe) where e1.idutilisateur ={idUtilisateur} order by idRessource asc")
    
    return result