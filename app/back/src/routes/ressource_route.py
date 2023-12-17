from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException


from src.config import config
from src.services.ressource_service import get_ressource_statement
import src.services.permision as perm

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

ressource = Blueprint('ressource', __name__)


@ressource.route('/ressource/getAll')
@jwt_required()
def getAll_ressource():
    """Renvoit toutes les ressources via la route /ressource/getAll

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table ressource
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table ressource
    
    :return:  toutes les resources
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    

    query = "select * from edt.ressource order by idressource asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@ressource.route('/ressource/add', methods=['POST'])
@jwt_required()
def addRessource() : 
    
    """Ajoute une ressource via la route /ressource/add

    :param Titre: titre de la ressource spécifié dans le body
    :type Titre: str

    :param NbrHeureSemestre: nombre d'heure de la ressource spécifié dans le body
    :type NbrHeureSemestre: int

    :param CodeCouleur: code couleur de la ressource spécifié dans le body
    :type CodeCouleur: str

    :param IdSemestre: id du semestre de la ressource spécifié dans le body
    :type IdSemestre: int

    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises ParamètreBodyManquantException: Si le body n'a pas pu être trouvé ou un paramètre est manquant dans le body

    :return:  ressource ajouté
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403

    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    if("Titre" not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Titre"))}), 400
    if('NbrHeureSemestre' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("NbrHeureSemestre"))}), 400
    if('CodeCouleur' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("CodeCouleur"))}), 400
    if('IdSemestre' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("IdSemestre"))}), 400
    if "Numero" not in json_datas.keys():
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Numero"))}), 400
    query = f"Insert into edt.ressource (titre, nbrheuresemestre, codecouleur, idsemestre , numero) values ('{json_datas['Titre']}', '{json_datas['NbrHeureSemestre']}', '{json_datas['CodeCouleur']}', '{json_datas['IdSemestre']}' , '{json_datas['Numero']}') returning idressource"
    conn = connect_pg.connect()
    try  :
        connect_pg.execute_commands(conn, query)
    except Exception as e: 
        return jsonify({'error': e}), 500
    connect_pg.disconnect(conn)
    return jsonify({'success': 'ressource added'}), 200


@ressource.route('/ressource/get/<id>', methods=['GET'])
@jwt_required()
def getRessource(id):
    """Renvoit une ressource spécifié par son id via la route /ressource/get/<id>
    
    :param id: id d'une ressource
    :type id: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table ressource
    
    :return:  la ressource a qui appartient cette userNidame
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    query = f"select * from edt.ressource where idressource = {id}"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@ressource.route('/ressource/update/<id>', methods=['PUT','GET'])
@jwt_required()
def UpdateRessource(id) :
    """Permet de mettre à jour une ressource spécifié par son id via la route /ressource/update/<id>
    
    :param id: id de la ressource à modifier
    :type id: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises ParamètreBodyManquantException: Si le body est manquant
    :raises ParamètreInvalideException: Si un paramètre est invalide
    
    :return:  la ressource a qui appartient cette userNidame
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    datas = request.get_json()
    print(datas.keys())
    if not datas:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    key = ["Titre", "NbrHeureSemestre", "CodeCouleur", "IdSemestre", "Numero"]
    for k in datas.keys():
        if k not in key:
            return jsonify({'erreur': str(apiException.ParamètreInvalideException(k))}), 400
    req = "UPDATE edt.ressource SET "
    for key in datas.keys():
        req += f"{key} = '{datas[key]}', "    
    
    #remove last comma
    if req[-2:] == ", ":
        req = req[:-2]
    req += f" WHERE idressource = {id}"
    
    con = connect_pg.connect()
    try:
        connect_pg.execute_commands(con, req)
    except Exception as e:
        return jsonify({'error': e}), 500
    
    return jsonify({'success': 'ressource updated'}), 200 