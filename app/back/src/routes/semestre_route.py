from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.semestre_service import get_semestre_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

semestre = Blueprint('semestre', __name__)


@semestre.route('/semestre/getAll')
@jwt_required()
def get_semestre():
    query = "select * from edt.semestre order by idsemestre asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_semestre_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("semestre"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@semestre.route('/semestre/add', methods=['POST'])
@jwt_required()
def add_semestre():
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400

    query = f"Insert into edt.semestre (numero) values ('{json_datas['Numero']}') returning idsemestre"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_datas['Numero'], "Numero", "semestre"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("semestre"))}), 500

    return jsonify(returnStatement)


@semestre.route('/semestre/get/<numeroSemestre>', methods=['GET', 'POST'])
@jwt_required()
def get_one_semestre(numeroSemestre):
    """Renvoit un semestre spécifié par son numéro via la route /semestre/get<numeroSemestre>

    :param numeroSemestre: numéro d'un semestre présent dans la base de donnée
    :type numeroSemestre: int

    :raises DonneeIntrouvableException: Impossible de trouver le semestre spécifié dans la table semestre
    :raises ParamètreTypeInvalideException: Le type de le numéro de semestre est invalide, un string est attendue

    :return: le semestre qui correspond au numéro entré en paramètre
    :rtype: json
    """

    query = f"select * from edt.semestre where numero='{numeroSemestre}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if not numeroSemestre.isdigit() or type(numeroSemestre) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("numeroSemestre", "string"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_semestre_statement(rows[0])
    except TypeError as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("semestre", numeroSemestre))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
