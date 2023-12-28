import src.connect_pg as connect_pg
import src.apiException as apiException
import flask

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  


def permissionCheck(userId , permissionNeeded , conn):
    """ Permet de vérifier si l'utilisateur a les permissions requise pour une action
    
    :param userId: id de l'utilisateur
    :type userId: int
    
    :param permissionNeeded: niveau de permession demandé (0 = admin , 1 = manager , 2 = teacher , 3 = student)
    :type permissionNeeded: String

    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: si l'utilisateur a les droits
    :rtype: bool
    """
    # Get user permission
    userPermission = getUserPermission(userId , conn)
    # Check if user has permission
    if userPermission <= permissionNeeded:
        return True
    else:
        return False
    
    
def getUserPermission(user_id , conn):
    """ Permet de récupérer les permissions d'un utilisateur 
    
    :param userId: id de l'utilisateur
    :type userId: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: le niveau de permission de l'utilisateur (0 = admin , 1 = manager , 2 = teacher , 3 = student)
    :rtype: int
    """
    # Get user permission check if the id user is in admin then if is the id is in manager then if is the id is in teacher
    
    result = connect_pg.get_query(conn , f"SELECT * FROM edt.admin WHERE idutilisateur ={user_id}")
    if result != []:
        return 0
    else:
        result = connect_pg.get_query(conn , f"SELECT idprof FROM edt.professeur WHERE idutilisateur = {user_id}")
        if result != []:
            result = connect_pg.get_query(conn , f"SELECT * FROM edt.manager WHERE idutilisateur = {result[0][0]}")
            if result != []:
                return 1
            return 2
        else:
            return 3
                

def estResponsableRessource(idRessource, idUtilisateur , conn):
    """ Permet de récupérer les permissions d'un utilisateur 
    
    :param userId: id de l'utilisateur
    :type userId: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: le niveau de permission de l'utilisateur (0 = admin , 1 = manager , 2 = teacher , 3 = student)
    :rtype: int
    """
    # Get user permission check if the id user is in admin then if is the id is in manager then if is the id is in teacher
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    if idProf == None:
        return False
    result = connect_pg.get_query(conn , f"SELECT * FROM edt.responsable WHERE idProf ={idProf} and idRessource={idRessource}")
    if result != []:
        return True
    else:
        return False


def estProfesseur(idUtilisateur , conn):
    """ Permet de récupérer les permissions d'un utilisateur 
    
    :param userId: id de l'utilisateur
    :type userId: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: le niveau de permission de l'utilisateur (0 = admin , 1 = manager , 2 = teacher , 3 = student)
    :rtype: int
    """
    # Get user permission check if the id user is in admin then if is the id is in manager then if is the id is in teacher
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    return idProf != None

def estEnseignantCours(idCours, idUtilisateur , conn):
    """ Permet de récupérer les permissions d'un utilisateur 
    
    :param userId: id de l'utilisateur
    :type userId: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: le niveau de permission de l'utilisateur (0 = admin , 1 = manager , 2 = teacher , 3 = student)
    :rtype: int
    """
    # Get user permission check if the id user is in admin then if is the id is in manager then if is the id is in teacher
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    if idProf == None:
        return False
    result = connect_pg.get_query(conn , f"SELECT * FROM edt.enseigner WHERE idProf ={idProf} and idCours={idCours}")
    if result != []:
        return True
    else:
        return False


    
    
    