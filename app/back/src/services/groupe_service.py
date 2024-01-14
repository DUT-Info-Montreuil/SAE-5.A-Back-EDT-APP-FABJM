
import src.connect_pg as connect_pg

def get_groupe_statement(row):
    """
    Fonction de mappage de la table groupe

    :param row: donnée représentant un groupe
    :type row: tableau

    :return: les données représentant un groupe
    :rtype: dictionnaire
    """
    return {
        'IdGroupe': row[0],
        'Nom': row[1],
        'AnneeScolaire': row[2],
        'Annee': row[3],
        'idGroupe_parent': row[4],
    }


def getGroupeProf(idUtilisateur , conn):
    """ Renvoie les groupes au quelle enseigne un professeur
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les groupes
    :rtype: list
    """
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    result = connect_pg.get_query(conn , f"Select edt.groupe.* from edt.groupe inner join edt.etudier using(idGroupe) inner join edt.enseigner as e2 using(idCours) where e2.idProf = {idProf} order by IdGroupe asc")
    
    return result
