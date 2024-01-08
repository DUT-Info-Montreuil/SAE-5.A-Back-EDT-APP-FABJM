from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.equipement_service import get_equipement_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error
import src.services.permision as perm

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
equipement = Blueprint('equipement', __name__)


@equipement.route('/equipement/getAll', methods=['GET'])
@jwt_required()
def get_all_equipement():
    """Renvoit tous les equipements via la route /equipement/getAll

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route
    
    :return:  tous les equipements
    :rtype: json
    """
    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)

    if(permision == 3):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"SELECT * from edt.equipement"

    equipements = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("equipement"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@equipement.route('/equipement/get/<filtre>', methods=['GET','POST'])
@jwt_required()
def get_equipement(filtre):
    """Renvoit les équipements remplisant les critères d'un filtre spécifié par son via la route /equipement/get/<filtre>
    
    :param filtre: peut-être l'id de l'équipement ou un nom au format string avec LIKE
    :type filtre: str, int
    
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé correspont aux critère
    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route
    
    :return: Les équipements filtrés
    :rtype: json
    """

    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)

    if(permision == 3):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    if filtre.isdigit():
        query = f"SELECT * from edt.equipement where idEquipement='{filtre}'"
    else:
        query = f"SELECT * from edt.equipement where Nom LIKE '%{filtre}%'"

    equipements = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("equipement"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@equipement.route('/equipement/add', methods=['POST'])
@jwt_required()
def add_equipement():
    """Permet d'ajouter un ou plusieurs equipements via la route /equipement/add

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route

    :return: un tableau d'id d'equipement crééent
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400


    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)

    if(permision != 0):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = "INSERT INTO edt.equipement (Nom)  VALUES " # OUTPUT inserted.idEquipement
    value_query = []
    for data in json_datas['data']:
        value_query.append(f"('{data['Nom']}')")
    query += ",".join(value_query)

    print(query)
    returnStatement = connect_pg.execute_commands(conn, query)
    tabIdEquipement = returnStatement
    print(tabIdEquipement)

    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipements with the ids  were successfully created"}), 200    #{', '.join(tabIdEquipement)}

@equipement.route('/equipement/update/<idEquipement>', methods=['POST'])
@jwt_required()
def update_equipement(idEquipement):
    """
    Permet de mettre à jour un equipement via la route /equipement/update/<idEquipement>

    :param idEquipement: l'id d'un equipement présent dans la base de donnée
    :type idEquipement: str

    :raises DonneeIntrouvableException: Impossible de trouver le equipement spécifié dans la table equipement

    :return: success
    :rtype: json
    """
    