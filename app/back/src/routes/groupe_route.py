from flask import Blueprint, request, jsonify
from flask_cors import CORS
import flask

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

import src.services.permision as perm

from src.services.groupe_service import get_groupe_statement

groupe = Blueprint('groupe', __name__)


@groupe.route('/groupe/getAll', methods=['GET'])
@jwt_required()
def get_groupe():
    """Renvoit tous les groupes via la route /groupe/getAll

    :return:  tous les groupes
    :rtype: json
    """
    conn = connect_pg.connect()
    if(perm.getUserPermission(get_jwt_identity() , conn) == 2):
        groupes = getEnseignantGroupe(get_jwt_identity() , conn)
        returnStatement = []
        try:
            for row in groupes:
                returnStatement.append(get_groupe_statement(row))
        except(TypeError) as e:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("groupe"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)

    query = "select * from edt.groupe order by IdGroupe asc"
    
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_groupe_statement(row))
    except(TypeError) as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("groupe"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

def getEnseignantGroupe(idUtilisateur , conn):
    """ Renvoie les groupes au quelle enseigne un professeur
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les groupes
    :rtype: list
    """
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    result = connect_pg.get_query(conn , f"Select edt.groupe.* from edt.groupe inner join edt.etudier using(idGroupe) inner join edt.enseigner as e2 using(idCours) where e2.idProf = {idProf} order by IdGroupe asc")
    
    return result


@groupe.route('/cours/getGroupeCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_groupe_cours(idCours):
    """Renvoit le groupe d'un cours via la route /cours/getGroupeCours/<idCours>
    
    :param idCours: id du groupe à rechercher
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises InsertionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    
    :return: le groupe
    :rtype: flask.wrappers.Response
    """
    returnStatement = []
    conn = connect_pg.connect()
    query = f"Select edt.groupe.* from edt.groupe inner join edt.etudier using(idGroupe)  inner join edt.cours as e1 using (idCours) where e1.idCours = {idCours} order by idGroupe asc"
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Etudier"))}), 400
        for row in rows:
            returnStatement.append(get_groupe_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("Etudier", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/ajouterCours/<idGroupe>', methods=['POST', 'PUT'])
@jwt_required()
def ajouterCours(idGroupe):
    """Permet d'ajouter un cours à un groupe via la route /groupe/ajouterCours/<idGroupe>
    
    :param idCours: id du cours à ajouter spécifié dans le body
    :type idCours: int

    :param idGroupe: id du groupe qui doit recevoir un cours
    :type idGroupe: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours ou idGroupe est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si une des clées n'a pas pu être trouvé
    :raises InsertionImpossibleException: Impossible de réaliser l'insertion

    :return: id du groupe
    :rtype: flask.wrappers.Response(json)
    """
    json_datas = request.get_json()
    if (not idGroupe.isdigit() or type(json_datas['idCours']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idGroupe", "numérique"))}), 400
    
    
    if 'idCours' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    returnStatement = {}
    query = f"Insert into edt.etudier (idGroupe, idCours) values ('{idGroupe}', '{json_datas['idCours']}') returning idGroupe"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "cours" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", json_datas['idCours']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Groupe ", idGroupe))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idGroupe = {idGroupe} et idCours = {json_datas['idCours']}"
            messageColonne = f"idGroupe et idCours"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "Etudier"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("Etudier"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/get/<idGroupe>', methods=['GET'])
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
    result = getEnseignantGroupe(get_jwt_identity() , conn)
    verification = False
    for row in result:
        if str(row[0]) == idGroupe:
            verification = True

    if not verification:
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 404
        
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    try:
        if len(rows) > 0:
            returnStatement = get_groupe_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/parent/get/<idGroupe>', methods=['GET'])
@jwt_required()
def get_parent_groupe(idGroupe):
    """Renvoit le parent du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe=(select idGroupe_parent from edt.groupe where idGroupe = '{idGroupe}')"

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


@groupe.route('/groupe/children/get/<idGroupe>', methods=['GET'])
@jwt_required()
def get_all_children(idGroupe):
    """Renvoit le parent du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """

    query = f"select * from edt.groupe where idGroupe_parent={idGroupe}"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    try:
        if len(rows) > 0:
            returnStatement = ""
            for row in rows:
                returnStatement += f"{get_groupe_statement(row)}"
    except TypeError as e:
        print(f"ERRRRRRRRRRRRRRRRRRRROR : {e}")
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
    if "idGroupe_parent" in json_datas.keys():
        query_start += ", idGroupe_parent"
        query_values += f", {json_datas['idGroupe_parent']}"
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
    return jsonify({"success": f"The group with id {idGroupe} was successfully created"}), 200


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
                               f"removed"}), 200


@groupe.route('/groupe/update/<idGroupe>', methods=['PUT'])
@jwt_required()
def update_groupe(idGroupe):
    """
    Permet de mettre à jour un groupe via la route /groupe/update/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return: success
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    key = ["Nom", "AnneeScolaire", "Annee", "idGroupe_parent"]
    for k in json_datas.keys():
        if k not in key:
            return jsonify({'error': "missing or invalid key"}), 400
    req = "UPDATE edt.groupe SET "
    for k in json_datas.keys():
        req += f"{k}='{json_datas[k]}', "

    if req[-2:] == ", ":
        req = req[:-2]
    req += f" WHERE idGroupe={idGroupe} RETURNING *"

    print("updateGroupe request : " + req)
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, req)
    except TypeError as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
    connect_pg.disconnect(conn)
    return jsonify({"success": f"the group with id {idGroupe} was successfully updated"}), 200
