from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.semestre_service import get_semestre_statement
import src.services.permision as perm
from src.routes.ressource_route import supprimer_ressource


import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

semestre = Blueprint('semestre', __name__)
# TODO: Finir semestre et refactor

@semestre.route('/semestre/getAll', methods=['GET'])
@jwt_required()
def get_semestre():
    """Renvoit tous les semestre via la route /semestre/getAll
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table semestre
    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table semestre
    
    :return: tous les semestres
    :rtype: json

    """

    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
        
    query = "SELECT * from edt.semestre order by idsemestre asc"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("semestre"))}), 404
        for row in rows:
            returnStatement.append(get_semestre_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("semestre", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@semestre.route('/semestre/add', methods=['POST'])
@jwt_required()
def add_semestre():
    """Permet d'ajouter un semestre via la route /semestre/add
    
    :param Numero: numero du semestre
    :type Numero: String
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour ajouter des données dans la table semestre
    :raises DonneeExistanteException: Les données entrée existe déjà dans la table semestre
    :raises ActionImpossibleException: Impossible d'ajouter le semestre spécifié dans la table semestre
    :raises ParamètreBodyManquantException: Le body requis n'a pas pu être trouvé
    
    :return: l'id du semestre crée
    :rtype: json

    """
    
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403


    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': str(apiException.ParamètreBodyManquantException())}), 400

    query = f"Insert into edt.semestre (numero) values ('{json_data['Numero']}') returning idsemestre"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except Exception as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_data['Numero'], "Numero", "semestre"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("semestre"))}), 500

    return jsonify({"success" : "semestre was added"}), 200


@semestre.route('/semestre/get/<numeroSemestre>', methods=['GET', 'POST'])
@jwt_required()
def get_one_semestre(numeroSemestre):
    """Renvoit un semestre spécifié par son numéro via la route /semestre/get<numeroSemestre>

    :param numeroSemestre: numéro d'un semestre présent dans la base de donnée
    :type numeroSemestre: int

    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer un semestre présents dans la table semestre
    :raises DonneeIntrouvableException: Impossible de trouver le semestre spécifié dans la table semestre
    :raises ParamètreTypeInvalideException: Le type de le numéro de semestre est invalide, un string est attendue

    :return: le semestre qui correspond au numéro entré en paramètre
    :rtype: json
    """


    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403


    query = f"SELECT * from edt.semestre where numero='{numeroSemestre}'"

    conn = connect_pg.connect()
    
    returnStatement = {}
    if not numeroSemestre.isdigit() or type(numeroSemestre) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("numeroSemestre", "string"))}), 400
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("etudier"))}), 404
        returnStatement = get_semestre_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200

@semestre.route('/semestre/supprimer/<idSemestre>', methods=['DELETE'])
@jwt_required()
def supprimer_semestre(idSemestre):
    """Permet de supprimer un semestre via la route /semestre/supprimer/<idSemestre>
    
    :param idSemestre: id du semestre à supprimer
    :type idSemestre: int

    :raises ActionImpossibleException: Impossible de supprimer le semestre spécifié dans la table semestre
    
    :return: message de succès
    :rtype: str
    """
    conn = connect_pg.connect()
    query = f"select idRessource from edt.ressource where idSemestre={idSemestre}"
    try:
        returnStatement = connect_pg.get_query(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("ressource","récupérer"))}), 500
    
    for k in range(len(returnStatement)):
        for i in range(len(returnStatement[k])):
            supprimer_ressource(str(returnStatement[k][i]) )

    query2 = f"delete from edt.ressource where idSemestre={idSemestre}"
    query = f"delete from edt.semestre where idSemestre={idSemestre}"
    
    try:
        connect_pg.execute_commands(conn, query2)
        connect_pg.execute_commands(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("semestre","supprimé"))}), 500
    
    return jsonify({'success': 'semestre supprimé'}), 200


@semestre.route('/semestre/update/<idSemestre>', methods=['PUT','GET'])
@jwt_required()
def upadateSemestre(idSemestre):
    """Permet de mettre à jour un semestre via la route /semestre/update/<numeroSemestre>

    :param numeroSemestre: numéro d'un semestre présent dans la base de donnée
    :type numeroSemestre: int

    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour mettre à jour un semestre présents dans la table semestre
    :raises DonneeIntrouvableException: Impossible de trouver le semestre spécifié dans la table semestre
    :raises ParamètreTypeInvalideException: Le type de le numéro de semestre est invalide, un string est attendue
    :raises InsertionImpossibleException: Impossible de mettre à jour le semestre spécifié dans la table semestre

    :return: le semestre qui correspond au numéro entré en paramètre
    :rtype: json
    """

   
    
    conn = connect_pg.connect()
    
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        print("get rekt")
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403


    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': str(apiException.ParamètreBodyManquantException())}), 400

    query = f"update edt.semestre set numero='{json_data['Numero']}' where IdSemestre='{idSemestre}'"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_data['Numero'], "Numero", "semestre"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("semestre"))}), 500

    return jsonify({"success" : "semestre was updated"}), 200




@semestre.route('/semestre/delete/<idSemestre>', methods=['DELETE'])
@jwt_required()
def deleteSemestre(idSemestre):

    """Permet de supprimer un semestre via la route /semestre/delete/<idSemestre>

    :param idSemestre: id d'un semestre présent dans la base de donnée
    :type idSemestre: int

    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour supprimer un semestre présents dans la table semestre
    :raises DonneeIntrouvableException: Impossible de trouver le semestre spécifié dans la table semestre
    :raises ParamètreTypeInvalideException: Le type de l'id de semestre est invalide, un int est attendue
    :raises InsertionImpossibleException: Impossible de supprimer le semestre spécifié dans la table semestre

    :return: le semestre qui correspond au numéro entré en paramètre
    :rtype: json
    """

    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"delete from edt.semestre where IdSemestre='{idSemestre}'"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(idSemestre, "idSemestre", "semestre"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("semestre"))}), 500

    return jsonify({"success" : "semestre was deleted"}), 200