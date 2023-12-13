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


@cours.route('/cours/get/<filtre>', methods=['GET','POST'])
def get_cours(filtre):
    """Renvoit les cours remplisant les critères d'un filtre spécifié par son via la route /cours/get/<filtre>
    
    :param filtre: peut-être l'id du cours ou un jour au format aaaa-mm-jj, si le filtre == "null" aucun filtre est appliqué
    :type filtre: str, int
    
    :raises ParamètreInvalideException: Le paramètre filtre est invalide
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé correspont aux critère
    
    :return: Les cours filtrés
    :rtype: json
    """
    if filtre.isdigit():
        query = f"select * from edt.cours where idCours='{filtre}'"

    elif len(filtre) == 10 and len(filtre.split("-")) == 3 : 
        query = f"select * from edt.cours where jour='{filtre}'"

    elif filtre == "null":
        query = f"select * from edt.cours"

    else:
        return jsonify({'error': str(apiException.ParamètreInvalideException("filtre"))}), 400

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/deplacer/<idCours>', methods=['PUT'])
def deplacer_cours(idCours):
    """Permet de supprimer un cours via la route /cours/delete
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours supprimer si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    json_datas = request.get_json()
    
    if 'HeureDebut' not in json_datas and 'Jour' not in json_datas:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    else:
        query = "UPDATE edt.cours "
        if 'HeureDebut' in json_datas:
            query += f"SET HeureDebut = '{json_datas['HeureDebut']}'"
        if 'Jour' in json_datas:
            if 'HeureDebut' in json_datas:
                query += f" , Jour = '{json_datas['Jour']}'"
            else:
                query += f"SET Jour = '{json_datas['Jour']}'"
        query += f" where idCours={idCours}"
        conn = connect_pg.connect()
        connect_pg.execute_commands(conn, query)
        connect_pg.disconnect(conn)
        return jsonify(idCours)

@cours.route('/cours/delete/<idCours>', methods=['DELETE'])
def delete_cours(idCours):
    """Permet de supprimer un cours via la route /cours/delete
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours supprimer si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    else:
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
    :raises ParamètreBodyManquantException: Si ou plusieurs paramètres sont manquant dans le body
    
    :return: le cours qui vient d'être créé
    :rtype: json
    """
    json_datas = request.get_json()
    if 'HeureDebut' not in json_datas or 'NombreHeure' not in json_datas or 'Jour' not in json_datas or 'idRessource' not in json_datas:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
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