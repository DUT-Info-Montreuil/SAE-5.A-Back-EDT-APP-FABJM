from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.equipement_route import get_equipement_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error
import src.services.permision as perm

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
equipement = Blueprint('equipement', __name__)


@equipement.route('/equipement/get/<filtre>', methods=['GET','POST'])
@jwt_required()
def get_equipement(filtre):
    """Renvoit les équipements remplisant les critères d'un filtre spécifié par son via la route /equipement/get/<filtre>
    
    :param filtre: peut-être l'id de l'équipement ou un nom au format string avec LIKE
    :type filtre: str, int
    
    :raises ParamètreInvalideException: Le paramètre filtre est invalide
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé correspont aux critère
    
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
        query = f"SELECT * from edt.equipement where Nom LIKE '%{nom}%'"
    equipements = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("equipement"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

    
    

