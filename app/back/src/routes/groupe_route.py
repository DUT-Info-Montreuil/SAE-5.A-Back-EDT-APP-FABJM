from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

from src.services.groupe_service import get_groupe_statement

groupe = Blueprint('groupe', __name__)


@groupe.route('/groupe/getAll', methods=['GET', 'POST'])
@jwt_required()
def get_groupe():
    """Renvoit tous les utilisateurs via la route /utilisateurs/get

    :return:  tous les utilisateurs
    :rtype: json
    """
    query = "select * from edt.groupe order by IdGroupe asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_groupe_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("groupe"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/get/<idGroupe>', methods=['GET', 'POST'])
@jwt_required()
def get_one_groupe(idGroupe):
    """Renvoit un utilisateur spécifié par son userName via la route /utilisateurs/get<userName>

    :param userName: nom d'un utilisateur présent dans la base de donnée
    :type userName: str

    :raises DonneeIntrouvableException: Impossible de trouver l'userName spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’userName est invalide, un string est attendue

    :return:  l'utilisateur a qui appartient cette userName
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe='{idGroupe}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if not idGroupe.isdigit() or type(idGroupe) is str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "int"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_groupe_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/parent/get/<idGroupe>', methods=['GET', 'POST'])
@jwt_required()
def get_parent_groupe(idGroupe):
    """Renvoit un utilisateur spécifié par son userName via la route /utilisateurs/get<userName>

    :param userName: nom d'un utilisateur présent dans la base de donnée
    :type userName: str

    :raises DonneeIntrouvableException: Impossible de trouver l'userName spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’userName est invalide, un string est attendue

    :return:  l'utilisateur a qui appartient cette userName
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe_1='{idGroupe}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if not idGroupe.isdigit() or type(idGroupe) is str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "int"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_groupe_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/add', methods=['POST'])
@jwt_required()
def add_groupe():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add

    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises InsertionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur

    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    queryStart = "Insert into edt.groupe (Nom, AnneeScolaire, Annee"
    queryValues = f"values ('{json_datas['Nom']}', '{json_datas['AnneeScolaire']}', '{json_datas['Annee']}'"
    if "idGroupe_1" in json_datas.keys():
        queryStart += ", idGroupe_1"
        queryValues += f", {json_datas['idGroupe_1']}"
    queryStart += ") "
    queryValues += ") returning IdUtilisateur"
    query = queryStart + queryValues
    print("addGroupe request : " + query)
    conn = connect_pg.connect()
    returnStatement = connect_pg.execute_commands(conn, query)

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)