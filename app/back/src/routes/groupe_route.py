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
    """Renvoit tous les groupes via la route /groupe/getAll

    :return:  tous les groupes
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
    """
    Renvoit un groupe spécifié par son idGroupe via la route /groupe/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver l'idGroupe spécifié dans la table groupe

    :return:  le groupe a qui appartient cet id
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe='{idGroupe}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
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
    """Renvoit le parent du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe=(select idGroupe_1 from edt.groupe where idGroupe = '{idGroupe}')"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    try:
        if len(rows) > 0:
            returnStatement = get_groupe_statement(rows[0])
    except TypeError as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/add', methods=['POST'])
@jwt_required()
def add_groupe():
    """Permet d'ajouter un groupe via la route /groupe/add

    :raises InsertionImpossibleException: Impossible d'ajouter le groupe spécifié dans la table groupe

    :return: l'id du groupe créé
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    query_start = "Insert into edt.groupe (Nom, AnneeScolaire, Annee"
    query_values = f"values ('{json_datas['Nom']}', '{json_datas['AnneeScolaire']}', '{json_datas['Annee']}'"
    if "idGroupe_1" in json_datas.keys():
        query_start += ", idGroupe_1"
        query_values += f", {json_datas['idGroupe_1']}"
    query_start += ") "
    query_values += ") returning idGroupe"
    query = query_start + query_values
    print("addGroupe request : " + query)
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idGroupe = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_datas['Nom'], "Nom", "groupe"))}), 400
        else:
            print("ERROR : " + e.pgcode)
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("groupe"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/delete/<idGroupe>', methods=['DELETE'])
@jwt_required()
def delete_groupe(idGroupe):
    """
    Permet de supprimer un groupe via la route /groupe/delete/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """
    conn = connect_pg.connect()
    query = f"DELETE from edt.groupe WHERE idgroupe={idGroupe} RETURNING *"
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify({"success": f"The group with id {idGroupe} and all subgroups from this group were successfully "
                               f"removed"})

