from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.user_service import get_utilisateur_statement
import src.services.permision as perm
import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
user = Blueprint('user', __name__)


@user.route('/utilisateurs/getAll', methods=['GET','POST'])
@jwt_required()
def get_utilisateur():
    """Renvoit tous les utilisateurs via la route /utilisateurs/get
    
    :return:  tous les utilisateurs
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    query = "select * from edt.utilisateur order by IdUtilisateur asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_utilisateur_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/get/<userName>', methods=['GET','POST'])
@jwt_required()
def get_one_utilisateur(userName):
    """Renvoit un utilisateur spécifié par son userName via la route /utilisateurs/get<userName>
    
    :param userName: nom d'un utilisateur présent dans la base de donnée
    :type userName: str
    
    :raises DonneeIntrouvableException: Impossible de trouver l'userName spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’userName est invalide, un string est attendue
    
    :return:  l'utilisateur a qui appartient cette userName
    :rtype: json
    """
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    query = f"select * from edt.utilisateur where Username='{userName}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if (userName.isdigit() or type(userName) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("userName", "string"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_utilisateur_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", userName))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/add', methods=['POST'])
@jwt_required()
def add_utilisateur():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    
    :raises InsertionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur crée
    :rtype: json

    { "role": "eleve", "users": [ { "firstName": "Elève1", "lastName": "lastName", "info": { "idGroupe": "1", "idSalle": "", "isManager": "" } }, { "firstName": "Elève2", "lastName": "lastName", "info": { "idGroupe": "2", "idSalle": "", "isManager": "" } } ] } 
    """
    #check if the user is admin
    conn = connect_pg.connect()
    json_datas = request.get_json()
    # if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
    #     return jsonify({'error': 'not enough permission'}), 403
    
    if not json_datas:
            return jsonify({'error ': 'missing json body'}), 400
    
    if (json_datas['role'] != "admin" and json_datas['role'] != "professeur" and json_datas['role'] != "eleve" and json_datas['role'] != "manager"):
        return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    
    for user in json_datas['users']:
        conn = connect_pg.connect()

        if "info" not in user.keys():
            return jsonify({'error': 'missing "info" part of the body'}), 400
        
        
        key = ["FirstName", "LastName", "Username", "Password"]
        for k in user.keys():
            if k in key:
                key.remove(k) 
        if len(key) != 0:
            return jsonify({'error ': 'missing ' + str(key)}), 400 

        query = f"Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{user['FirstName']}', '{user['LastName']}', '{user['Username']}', '{user['Password']}') returning IdUtilisateur"
        conn = connect_pg.connect()
        try:
            returnStatement = connect_pg.execute_commands(conn, query)
            idUser = returnStatement
        except psycopg2.IntegrityError as e:
            if e.pgcode == errorcodes.UNIQUE_VIOLATION:
                # Erreur violation de contrainte unique
                return jsonify({'error': str(apiException.DonneeExistanteException(user['Username'], "Username", "utilisateur"))}), 400
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 500

        
        try : 
            
            #switch case pour le role
            if json_datas['role'] == "admin":
                query = f"Insert into edt.admin (IdUtilisateur) values ({idUser}) returning IdUtilisateur"
            elif json_datas['role'] == "professeur":
                query = f"Insert into edt.professeur (initiale , idsalle , Idutilisateur) values ('{user['info']['initiale']}' , '{user['info']['idsalle']}' ,'{idUser}') returning idProf" 
                
            elif json_datas['role'] == "eleve":
                query = f"Insert into edt.Eleve (idgroupe , Idutilisateur) values ('{user['info']['idgroupe']}' , '{idUser}')returning IdUtilisateur"
            returnStatement = connect_pg.execute_commands(conn, query)
            
            if json_datas['role'] == "professeur":
                if(user['info']['isManager'] ):
                    query = f"Insert into edt.manager (IdProf) values ({returnStatement}) returning IdUtilisateur"
                    returnStatement = connect_pg.execute_commands(conn, query)
                
                

            
            
        except Exception as e :
            print(e)
            connect_pg.disconnect(conn)
            conn = connect_pg.connect()
            query =f'delete from edt.utilisateur where idutilisateur = {idUser}'
            returnStatement = connect_pg.execute_commands(conn , query)
            return jsonify({"error" : "info part is wrong "}) , 400
        finally : 
            connect_pg.disconnect(conn)

    return jsonify({"success" : "user was added"}), 200

@user.route('/utilisateurs/auth', methods=['GET'])
def auth_utilisateur():
    """ Permet d'authentifier un utilisateur via la route /utilisateurs/auth
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    
    :param PassWord: mot de passe de l'utilisateur spécifié dans le body
    :type PassWord: String

    :raises DonneeIntrouvableException: Impossible de trouver l'Username spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’Username est invalide
    
    :return: jwt token
    :rtype: str
    """
    
    json_datas = request.get_json()
    username = json_datas['Username']
    password = json_datas['Password']
    query = f"select Password, FirstLogin , idutilisateur from edt.utilisateur where Username='{username}'"
    conn = connect_pg.connect()
    
    rows = connect_pg.get_query(conn, query)
    
    if (username.isdigit() or type(username) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("username", "string"))}), 400
    if (not rows):
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", username))}), 404
    
    
    if (rows[0][0] == password):
       accessToken =  create_access_token(identity=rows[0][2])
       return jsonify(accessToken=accessToken, firstLogin=rows[0][1])
   
    return jsonify({'error': str(apiException.LoginOuMotDePasseInvalideException())}), 400


#firstLogin route wich update the password and the firstLogin column
@user.route('/utilisateurs/firstLogin', methods=['POST'])
@jwt_required()
def firstLogin_utilisateur():
    """ Permet à un utilisateur de définir un mot de passe lors de la première connexion via la route /utilisateurs/firstLogin
    
    :param password: mot de passe définie par le nouvel utilisateur spécifié dans le body
    :type password: String

    :raises ParamètreTypeInvalideException: Le type de password doit être un string non vide
    :raises InsertionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    

    """
    username = get_jwt_identity()
    json_datas = request.get_json()
    password = json_datas['Password']
    if(password == ""):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("password", "string"))}), 400    
    query = f"update edt.utilisateur set PassWord='{password}', FirstLogin=false where idutilisateur='{id}'"
    conn = connect_pg.connect()
    try:
        
        connect_pg.execute_commands(conn, query)
    except:
        return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 500
    connect_pg.disconnect(conn)
    
    
        
    
@user.route('/utilisateurs/update/<id>', methods=['PUT','GET'])
@jwt_required()
def update_utilisateur(id):
    """Permet de modifier un utilisateur via la route /utilisateurs/update
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises InsertionImpossibleException: Impossible de modifier l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur modifié
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    if 'role' in json_datas.keys():
        return jsonify({'error ': 'le role ne peut pas etre modifié pour l\'instant'}), 400

        if (json_datas['role'] != "admin" and json_datas['role'] != "professeur" and json_datas['role'] != "eleve" and json_datas['role'] != "manager"):
            return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    
        if "info" not in json_datas.keys():
            return jsonify({'error': 'missing "info" part of the body'}), 400
    
    #req = "Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{json_datas['FirstName']}', '{json_datas['LastName']}', '{json_datas['Username']}', '{json_datas['Password']}') returning IdUtilisateur" 

    req = "update edt.utilisateur set "
    if 'FirstName' in json_datas.keys():
        req += f"firstname = '{json_datas['FirstName']}' , "
    if 'LastName' in json_datas.keys():
        req += f"lastname = '{json_datas['LastName']}' , "
    if 'Username' in json_datas.keys():
        req += f"username = '{json_datas['Username']}' , "
    if 'Password' in json_datas.keys():
        req += f"password = '{json_datas['Password']}'"
    
    #remove "and" if there is no update
    if req[-2:] == ", ":
        req = req[:-2]

    req += f" where idutilisateur={id}"
    #update edt.utilisateur set firstname = 'bastien2' where idutilisateur = 8
    
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, req)
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
           
            return jsonify({'error': str(apiException.DonneeExistanteException(json_datas['Username'], "Username", "utilisateur"))}), 400
        else:
            
            return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 500
    
    return jsonify({'success': 'utilisateur modifié'}), 200


@user.route('/utilisateurs/delete/<id>', methods=['GET','POST'])
@jwt_required()
def delete_utilisateur(id):
    """Permet de supprimer un utilisateur via la route /utilisateurs/delete
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises InsertionImpossibleException: Impossible de supprimer l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur supprimé
    :rtype: json
    """

    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    json_datas = request.get_json()
    query = f"delete from edt.utilisateur where idutilisateur={id}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        
       
        return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 500
    
    return jsonify({'success': 'utilisateur supprimé'}), 200

        
#TODO : DEBUG ROUTE TO DELETE 
@user.route('/utilisateurs/getPermission', methods=['GET','POST'])
@jwt_required()
def getPermission():
    """Permet de récupérer la permission d'un utilisateur via la route /utilisateurs/getPermission
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises InsertionImpossibleException: Impossible de récupérer la permission de l'utilisateur spécifié dans la table utilisateur
    
    :return: la permission de l'utilisateur
    :rtype: json
    """
    user_id = get_jwt_identity()
    conn = connect_pg.connect()
    return jsonify(perm.getUserPermission(user_id , conn))






    


