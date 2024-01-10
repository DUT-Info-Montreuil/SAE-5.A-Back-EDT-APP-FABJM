from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.salle_service import get_salle_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
salle = Blueprint('salle', __name__)


@salle.route('/salle/getAll')
@jwt_required()
def get_salle():
    """Renvoit toutes les salles via la route /salle/getAll

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table salle
    
    :return: toutes les salles
    :rtype: json
    """
    query = "select * from edt.salle order by idsalle asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("salle"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@salle.route('/salle/get/<idSalle>', methods=['GET', 'POST'])
@jwt_required()
def get_one_salle(idSalle):
    """Renvoit une salle spécifié par son id via la route /salle/get<idSalle>

    :param idSalle: id d'une salle présent dans la base de donnée
    :type idSalle: int

    :raises DonneeIntrouvableException: Impossible de trouver la salle spécifié dans la table salle
    :raises ParamètreTypeInvalideException: Le type de l'id salle est invalide, une valeur numérique est attendue

    :return: la salle qui correspond à l'id du numéro entré en paramètre
    :rtype: json
    """

    query = f"select * from edt.salle where idSalle='{idSalle}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if not idSalle.isdigit() or type(idSalle) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_salle_statement(rows[0])
    except TypeError as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("salle", idSalle))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200




@salle.route('/salle/delete/<idSalle>', methods=['DELETE'])
@jwt_required()
def delete_salle(idSalle):
    """Permet de supprimer une salle via la route /salle/delete/<idSalle>
    
    :param idSalle: id de la salle à supprimer
    :type idSalle: int

    :raises InsertionImpossibleException: Impossible de supprimer la salle spécifié dans la table salle
    
    :return: message de succès
    :rtype: str
    """
    query = f"delete from edt.salle where idSalle={idSalle}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("salle","supprimé"))}), 500
    
    return jsonify({'success': 'salle supprimé'}), 200

@salle.route('/salle/add', methods=['POST'])
@jwt_required()
def add_salle():
    """Permet d'ajouter une salle via la route /salle/add
    
    :param salle: salle à ajouter, spécifié dans le body
    :type salle: json

    :raises InsertionImpossibleException: Impossible d'ajouter la salle spécifié dans la table salle
    :raises DonneeExistanteException: Cette salle existe déjà
    
    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400

    query = f"Insert into edt.salle (Numero, Capacite) values ('{json_datas['Numero']}',{json_datas['Capacite']}) returning idSalle"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_datas['Numero'], "Numero", "salle"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("salle"))}), 500

    return jsonify({"success" : "la salle a été ajouté"}), 200




@salle.route('/salle/update', methods=['PUT'])
@jwt_required()
def update_salle():
    """Permet de modifier une salle via la route /salle/update
    
    :param salle: salle à modifier, spécifié dans le body
    :type salle: json

    :raises InsertionImpossibleException: Impossible de modifier la salle spécifié dans la table salle
    
    :return: message de succès
    :rtype: str
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    query = f"update edt.salle set Numero='{json_datas['Numero']}', Capacite={json_datas['Capacite']} where idSalle={json_datas['idSalle']}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("salle"))}), 500
    return jsonify({'success': 'salle modifié'}), 200