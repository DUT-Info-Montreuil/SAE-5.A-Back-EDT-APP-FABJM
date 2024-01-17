from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.equipement_service import get_equipement_statement
from src.services.salle_service import get_salle_statement

from src.utilitary import update

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

    :raises PermissionManquanteException: L'utilisateur n'a pas les droits pour avoir accés à cette route
    :raises AucuneDonneeTrouverException: Si aucune données remplisssant les critères n'a été trouvé 
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table équipements
    
    :return:  tous les equipements
    :rtype: json
    """
    conn = connect_pg.connect()
    
    if not (perm.permissionCheck(get_jwt_identity() , 3 , conn)):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"SELECT * from edt.equipement"

    
    returnStatement = []
    try:
        equipements = connect_pg.get_query(conn, query)
        if equipements == []:
            return jsonify([])
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "récupérer"))}), 500
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
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table équipements
    
    :return: Les équipements filtrés
    :rtype: json
    """

    conn = connect_pg.connect()
  

    if not (perm.permissionCheck(get_jwt_identity() , 3 , conn)):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    if filtre.isdigit():
        query = f"SELECT * from edt.equipement where idEquipement='{filtre}'"
    else:
        query = f"SELECT * from edt.equipement where Nom LIKE '%{filtre}%'"

    
    returnStatement = []
    try:
        equipements = connect_pg.get_query(conn, query)
        if equipements == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("equipement"))}), 404
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@equipement.route('/equipement/add', methods=['POST'])
@jwt_required()
def add_equipement():
    """Permet d'ajouter un ou plusieurs equipements via la route /equipement/add

    :raises PermissionManquanteException: L'utilisateur n'a pas les droits pour avoir accés à cette route
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table équipements

    :return: un tableau d'id d'equipement crééent
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400


    conn = connect_pg.connect()

   
    if not (perm.permissionCheck(get_jwt_identity() , 0 , conn)):

        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403
    query = "INSERT INTO edt.equipement (Nom) VALUES "
    value_query = []
    for data in json_data['data']:
        value_query.append(f"('{data['Nom']}')")
    query += ",".join(value_query) + " returning idEquipement"

    # TODO: find why only one id is return when multiple one are inserted
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        print(e)
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "ajouter"))}), 500

    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipements with the ids {returnStatement} were successfully created"}), 200    #{', '.join(tabIdEquipement)}

@equipement.route('/equipement/update/<idEquipement>', methods=['PUT'])
@jwt_required()
def update_equipement(idEquipement):
    """
    Permet de mettre à jour un equipement via la route /equipement/update/<idEquipement>

    :param idEquipement: l'id d'un equipement présent dans la base de donnée
    :type idEquipement: str

    :raises PermissionManquanteException: L'utilisateur n'a pas les droits pour avoir accés à cette route
    :raises ActionImpossibleException: Si une erreur est survenue lors de la suppression

    :return: success
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    table_name = "Equipement"
    keys = ["Nom"]
    
    query = update("Equipement", f"idEquipement={idEquipement}", json_data, keys)
    # Si query update return une error
    if type(query) == tuple:
        return query

    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)[0]
    if(permision != 0):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403
    
    try:
        connect_pg.execute_commands(conn, query[0], query[1])
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "mise à jour"))}), 500
    connect_pg.disconnect(conn)
    return jsonify({"success": f"the equipement with id {idEquipement} was successfully updated"}), 200

@equipement.route('/equipement/delete/<idEquipement>', methods=['DELETE'])
@jwt_required()
def delete_equipement(idEquipement):
    """
    Permet de supprimer un groupe via la route /groupe/delete/<idEquipement>

    :param idEquipement: l'id d'un groupe présent dans la base de donnée
    :type idEquipement: str

    :raises ActionImpossibleException: Si une erreur est survenue lors de la suppression

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """
    conn = connect_pg.connect()
    query = f"DELETE FROM edt.Equipement WHERE idEquipement={idEquipement} RETURNING *"
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "supprimer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipement with id {idEquipement} was successfully removed"}), 200


##################    Salle de Equipement    ####################
# TODO: Delete
@equipement.route('/equipement/get/salle/<idEquipement>', methods=['GET'])
@jwt_required()
def get_salles_of_equipement(idEquipement):
    """Renvoit tous les salles au quel l'equipement(avec l'idEquipement) est lié via la route /equipement/get/salle/<idEquipement>

    :param idEquipement: l'id d'un groupe présent dans la base de donnée
    :type idEquipement: str

    :raises PermissionManquanteException: L'utilisateur n'a pas les droits pour avoir accés à cette route
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return:  tous les equipements
    :rtype: json
    """
    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)[0]

    if(permision == 3):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"SELECT s.* from edt.equiper AS e NATURAL JOIN edt.salle AS s WHERE e.idEquipement={idEquipement}"

    equipements = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in equipements:
            returnStatement.append(get_salle_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@equipement.route('/equipement/add/salle/<idSalle>', methods=['POST'])
@jwt_required()
def add_salle_of_equipement(idSalle):
    """Permet d'ajouter une ou plusieurs salles a un équipement via la route /equipement/add/salle/<idEquipement>

    :param idEquipement: l'id d'un groupe présent dans la base de donnée
    :type idEquipement: str

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route

    :return: un tableau d'id d'equipement crééent
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400

    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)[0]

    if(permision != 0):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    StartQuery = "INSERT INTO edt.equiper (idEquipement, idSalle) VALUES "
    result = []
    #add multiple equipement 
    for data in json_data['data']:
        

        query = StartQuery + ","+f"({json_data["idEquipements"]},'{idSalle}')"+" returning idEquipement"

        try : 
          result.append(connect_pg.execute_commands(conn, query))
        except Exception as e:
          return jsonify({'error': str(apiException.ActionImpossibleException("equipement", "récupérer"))}), 500
        query = ""



    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipements with the ids {result} were successfully created"}), 200    #{', '.join(tabIdEquipement)}