from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.user_service import get_utilisateur_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

user = Blueprint('user', __name__)


@user.route('/utilisateurs/getAll', methods=['GET','POST'])
def get_utilisateur():
    """Renvoit tous les utilisateurs via la route /utilisateurs/get
    
    :return:  tous les utilisateurs
    :rtype: json
    """
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
def get_one_utilisateur(userName):
    """Renvoit un utilisateur spécifié par son id via la route /utilisateurs/get<userName>
    
    :param IdUtilisateur: id d'un utilisateur présent dans la base de donnée
    :type IdUtilisateur: Numérique
    
    :raises DonneeIntrouvableException: Impossible de trouver l'id spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’id est invalide
    
    :return:  l'utilisateur a qui appartient cette id
    :rtype: json
    """
    #query = "select * from utilisateur where IdUtilisateur=%(IdUtilisateur)s" % {'IdUtilisateur': userName}
    query = f"select * from utilisateur where Username='{userName}'"

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
def add_utilisateur():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add
    
    :param IdUtilisateur: donnée représentant un utilisateur
    :type IdUtilisateur: json
    
    :raises InsertionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    if "info" not in json_datas.keys():
        return jsonify({'error': 'missing "info" part of the body'}), 400
    if (json_datas['role'] != "admin" and json_datas['role'] != "professeur" and json_datas['role'] != "eleve" and json_datas['role'] != "manager"):
        return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    

    returnStatement = {}
    query = f"Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{json_datas['FirstName']}', '{json_datas['LastName']}', '{json_datas['Username']}', '{json_datas['Password']}') returning IdUtilisateur"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idUser = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(apiException.DonneeExistanteException(json_datas['Username'], "Username", "utilisateur"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("utilisateur"))}), 500

    
    try : 
        
        #switch case pour le role
        if json_datas['role'] == "admin":
            query = f"Insert into edt.admin (IdUtilisateur) values ({idUser}) returning IdUtilisateur"
        elif json_datas['role'] == "professeur":
            query = f"Insert into edt.professeur (initiale , idsalle , Idutilisateur) values ('{json_datas['info']['initiale']}' , '{json_datas['info']['idsalle']}' ,'{idUser}') returning IdUtilisateur"
        elif json_datas['role'] == "eleve":
            query = f"Insert into edt.Eleve (idgroupe , Idutilisateur) values ({json_datas['info']['idgroupe'] , idUser})returning IdUtilisateur"
        elif json_datas['role'] == "manager":
            userId = returnStatement
            query = f"Insert into edt.professeur (idgroupe  Idutilisateur) values ('{json_datas['info']['initiale']}' , '{json_datas['info']['idsalle']}' ,'{idUser}')returning idprof"
            returnStatement = connect_pg.execute_commands(conn, query)
            query = f"Insert into edt.manager (IdProf) values ({returnStatement}) returning IdUtilisateur"
            returnStatement = userId
        
        returnStatement = connect_pg.execute_commands(conn, query)
        
    except :
        connect_pg.disconnect(conn)
        conn = connect_pg.connect()
        query =f'delete from edt.utilisateur where idutilisateur = {idUser}'
        returnStatement = connect_pg.execute_commands(conn , query)
        return jsonify({"error" : "info part is wrong "}) , 400
    finally : 
        connect_pg.disconnect(conn)

    return jsonify(returnStatement)


    
    





    


