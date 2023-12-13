import src.connect_pg as connect_pg
import src.apiException as apiException

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  


def permissionCheck(userId , permissionNeeded , conn):
    """

    Args:
        userToken String : token of the user
        permissionNeeded (): level of permission needed (0 = admin , 1 = manager , 2 = teacher , 3 = student)
        conn (conn): connection to the database

    Returns:
        bool: if the user as level of permission needed
    """

    # Get user permission
    userPermission = getUserPermission(userId , conn)
    # Check if user has permission
    if userPermission <= permissionNeeded:
        return True
    else:
        return False
    
    
def getUserPermission(user_id , conn):
    # Get user permission check if the id user is in admin then if is the id is in manager then if is the id is in teacher
    
    result = connect_pg.get_query(conn , f"SELECT * FROM edt.admin WHERE idutilisateur ={user_id}")
    if result != []:
        return 0
    else:
        result = connect_pg.get_query(conn , f"SELECT * FROM edt.manager WHERE idutilisateur = {user_id}" )
        if result != []:
            return 1
        else:
            result = connect_pg.get_query(conn , f"SELECT * FROM edt.teacher WHERE idutilisateur = {user_id}")
            if result != []:
                return 2
            else:
                return 3
                
    
    
    