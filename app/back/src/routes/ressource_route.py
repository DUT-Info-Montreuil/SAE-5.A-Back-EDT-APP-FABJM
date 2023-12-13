from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.ressource_service import get_ressource_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

ressource = Blueprint('ressource', __name__)


@ressource.route('/ressource/getAll')
#@jwt_required()
def getAll_ressource():
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
    :param Titre: titre de la ressource
    :param NbrHeureSemestre: nombre d'heure de la ressource
    :param CodeCouleur: code couleur de la ressource
    :param IdSemestre: id du semestre de la ressource
    :return:  ressource ajouté
    :rtype: json
    """

    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    if("Titre" not in json_datas.keys()):
        return jsonify({'error': 'missing "Titre'}), 400
    if('NbrHeureSemestre' not in json_datas.keys()):
        return jsonify({'error': 'missing "NbrHeureSemestre'}), 400
    if('CodeCouleur' not in json_datas.keys()):
        return jsonify({'error': 'missing "CodeCouleur'}), 400
    if('IdSemestre' not in json_datas.keys()):
        return jsonify({'error': 'missing "IdSemestre'}), 400
    if "Numero" not in json_datas.keys():
        return jsonify({'error': 'missing "Numero'}), 400
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
    
    datas = request.get_json()
    print(datas.keys())
    if not datas:
        return jsonify({'error ': 'missing json body'}), 400
    key = ["Titre", "NbrHeureSemestre", "CodeCouleur", "IdSemestre", "Numero"]
    for k in datas.keys():
        if k not in key:
            return jsonify({'error': 'missing or invalid key'}), 400
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