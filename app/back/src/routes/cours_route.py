from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.cours_service import get_cours_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
cours = Blueprint('cours', __name__)



@cours.route('/cours/delete/<idCours>', methods=['DELETE'])
def delete_cours(idCours):
    """Permet de supprimer un cours via la route /cours/delete
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :return: id du cours supprimer si présent
    :rtype: json
    """
    query = "delete  from edt.cours where idCours=%(idCours)s" % {'idCours':idCours}
    conn = connect_pg.connect()
    connect_pg.execute_commands(conn, query)
    connect_pg.disconnect(conn)
    return jsonify(idCours)

@cours.route('/cours/add', methods=['POST'])
def add_cours():
    """Permet d'ajouter un cours via la route /cours/add
    
    :param cours: donnée représentant un cours spécifié dans le body
    :type cours: json
    
    :raises InsertionImpossibleException: Impossible d'ajouter le cours spécifié dans la table cours
    :raises DonneeIntrouvableException: La valeur de la clée étrangère idRessource n'a pas pu être trouvé
    
    :return: le cours qui vient d'être créé
    :rtype: json
    """
    json_datas = request.get_json()
    returnStatement = {}
    query = f"Insert into edt.cours (HeureDebut, NombreHeure, Jour, idRessource) values ('{json_datas['HeureDebut']}', '{json_datas['NombreHeure']}', '{json_datas['Jour']}', '{json_datas['idRessource']}') returning idCours"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_datas['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("cours"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)