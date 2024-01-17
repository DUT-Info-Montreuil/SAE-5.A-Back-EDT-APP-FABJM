

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
from src.services.cours_service import get_cours_statement

from src.services.groupe_service import get_groupe_statement, getGroupeProf
import src.services.verification as verif 
import datetime

import json

groupe = Blueprint('groupe', __name__)
# TODO: fix route get and test other

@groupe.route('/groupe/getAll', methods=['GET'])
@jwt_required()
def get_groupe():
    """Renvoit tous les groupes via la route /groupe/getAll

    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données

    :return:  tous les groupes
    :rtype: json
    """
    conn = connect_pg.connect()
    if (perm.getUserPermission(get_jwt_identity(), conn) == 2):
        returnStatement = []
        try:
            groupes = getGroupeProf(get_jwt_identity(), conn)
            if groupes == []:
                return jsonify({'error': str(apiException.AucuneDonneeTrouverException("groupes"))}), 404
            for row in groupes:
                returnStatement.append(get_groupe_statement(row))
        except Exception as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récupérer"))}), 500
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)

    query = "SELECT * from edt.groupe order by IdGroupe asc"
    
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        for row in rows:
            returnStatement.append(get_groupe_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)



@groupe.route('/cours/getGroupeCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_groupe_cours(idCours):
    """Renvoit le groupe d'un cours via la route /cours/getGroupeCours/<idCours>
    
    :param idCours: id du groupe à rechercher
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    :raises ParamètreTypeInvalideException: Si le paramètre idCours n'est pas une valeur numérique
    
    :return: le groupe
    :rtype: flask.wrappers.Response
    """

    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400

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
        return jsonify({'error': str(apiException.ActionImpossibleException("Etudier", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@groupe.route('/cours/getGroupeManager/<idManager>', methods=['GET','POST'])
@jwt_required()
def get_groupe_manager(idManager):
    """Renvoit le groupe d'un manager via la route /cours/getGroupeManager/<idManager>
    
    :param idManager: id du groupe à rechercher
    :type idManager: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    
    :return: le groupe
    :rtype: flask.wrappers.Response
    """

    if (not idManager.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idManager", "numérique"))}), 400

    returnStatement = {}
    conn = connect_pg.connect()
    query = f"Select edt.groupe.*  from edt.groupe inner join edt.manager using(idGroupe) where idManager = {idManager} order by idManager asc"
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Manager"))}), 400
        for row in rows:
            returnStatement = get_groupe_statement(rows[0])
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Groupe ou Manager", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/ajouterCours/<idGroupe>', methods=['POST', 'PUT'])
@jwt_required()
def ajouter_cours(idGroupe):
    """Permet d'ajouter un cours à un groupe via la route /groupe/ajouterCours/<idGroupe>
    
    :param idCours: id du cours à ajouter spécifié dans le body
    :type idCours: int

    :param idGroupe: id du groupe qui doit recevoir un cours
    :type idGroupe: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours ou idGroupe est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser l'insertion
    :raises ParamètreInvalideException: Si le groupe n'est pas disponible à l'horaire spécifié

    :return: id du groupe
    :rtype: flask.wrappers.Response(json)
    """
    from src.routes.cours_route import get_cours
    conn = connect_pg.connect()
    json_datas = request.get_json()

    if 'idCours' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if (not idGroupe.isdigit() or type(json_datas['idCours']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idGroupe", "numérique"))}), 400
    
    courGroupe = get_cours(str(json_datas['idCours']))
    if type(courGroupe) == tuple :
        return jsonify({'error': str(apiException.ActionImpossibleException("cours"))}), 500

    courGroupe = json.loads(get_cours(str(json_datas['idCours'])).data) 
    HeureDebut = courGroupe[0]['HeureDebut']
    NombreHeure = courGroupe[0]['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
    HeureFin = str(HeureDebut + NombreHeure)

    query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.etudier using(idCours)  where idGroupe = {idGroupe}
    and ((HeureDebut <= '{courGroupe[0]['HeureDebut']}' and '{courGroupe[0]['HeureDebut']}'::time <=  (HeureDebut + NombreHeure::interval))
    or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
    and ('{courGroupe[0]['Jour']}' = Jour and idCours is not null) order by idCours asc
    """

    result = connect_pg.get_query(conn , query)
    
    if result != []:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce groupe n'est pas disponible à la période spécifié"))}), 400
    
    returnStatement = {}
    query = f"Insert into edt.etudier (idGroupe, idCours) values ('{idGroupe}', '{json_datas['idCours']}') returning idGroupe"
    
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
            return jsonify({'error': str(apiException.ActionImpossibleException("Etudier"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@groupe.route('/groupe/enleverCours/<idCours>', methods=['DELETE'])
@jwt_required()
def enlever_Cours(idCours):
    """Permet d'enlever un cours attribuer à un groupe via la route /groupe/enleverCours/<idCours>
    
    :param idCours: id du cours à enlever
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si la clée spécifié pour la colonne idCours n'a pas pu être trouvé
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la suppression

    :return: id du cours supprimer si présent
    :rtype: flask.wrappers.Response(String)
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    query = f"delete from edt.etudier where idCours={idCours}"
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Etudier ", idCours))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("Etudier","supprimer"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(idCours)

@groupe.route('/groupe/getGroupeDispo', methods=['GET', 'POST'])
@jwt_required()
def get_groupe_dispo():
    """Renvoit tous les groupes disponible sur une période via la route /groupe/getGroupeDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) à spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la période au format TIME(hh:mm:ss) à spécifié dans le body
    :type NombreHeure: int

    :param Jour: date de la journée où la disponibilité des groupes doit être vérifer au format DATE(yyyy-mm-dd)
    :type Jour: str

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table groupe, etudier ou cours
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreInvalideException: Si un des paramètres est invalide
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: touts les groupes disponibles
    :rtype: flask.wrappers.Response(json)
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    
    if 'HeureDebut' not in json_datas or 'Jour' not in json_datas or 'NombreHeure' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if not verif.estDeTypeTime(json_datas['HeureDebut']) or not verif.estDeTypeDate(json_datas['Jour']) or not verif.estDeTypeTime(json_datas['NombreHeure']):
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure ou Jour"))}), 404

    HeureDebut = json_datas['HeureDebut']
    NombreHeure = json_datas['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
    HeureFin = HeureDebut + NombreHeure

    heure_ouverture_iut = datetime.timedelta(hours = 8)
    heure_fermeture_iut = datetime.timedelta(hours = 19)

    if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé durant la période spécifié"))}), 404


    query = f""" select distinct edt.groupe.*  from edt.groupe full join edt.etudier using(idGroupe) full join edt.cours
    using(idCours) where (idGroupe is not null) and ( '{json_datas['HeureDebut']}' <  HeureDebut 
    and  '{str(HeureFin)}' <= HeureDebut or '{json_datas['HeureDebut']}'::time >=  (HeureDebut + NombreHeure::interval))
    or ('{json_datas['Jour']}' != Jour and idGroupe is not null) or (HeureDebut is null) order by idGroupe asc
    """
    conn = connect_pg.connect()
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Aucun groupe disponible n'a été trouvé à la période spécifié"))}), 400
        
        for row in rows:
            returnStatement.append(get_groupe_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Etudier", "récupérer"))}), 500
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
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données

    :return:  le groupe a qui appartient cet id
    :rtype: json
    """
    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    query = f"SELECT * from edt.groupe where idGroupe='{idGroupe}'"
    conn = connect_pg.connect()
    result = getGroupeProf(get_jwt_identity(), conn)
    verification = False
    for row in result:
        if str(row[0]) == idGroupe:
            verification = True

    if not verification:
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403
        
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
        returnStatement = get_groupe_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/parent/get/<idGroupe>', methods=['GET'])
@jwt_required()
def get_parent_groupe(idGroupe):
    """Renvoit le parent du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """

    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    query = f"SELECT * from edt.groupe where idGroupe=(SELECT idGroupe_parent from edt.groupe where idGroupe = '{idGroupe}')"

    conn = connect_pg.connect()
    
    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
        returnStatement = get_groupe_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/children/get/<idGroupe>', methods=['GET'])
@jwt_required()
def get_all_children(idGroupe):
    """Renvoit le parent du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données

    :return:  le parent du groupe a qui appartient cet id
    :rtype: json
    """

    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    query = f"SELECT * from edt.groupe where idGroupe_parent={idGroupe}"

    conn = connect_pg.connect()
    
    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("groupe", idGroupe))}), 404
        returnStatement = ""
        for row in rows:
            returnStatement += f"{get_groupe_statement(row)}"
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@groupe.route('/groupe/add', methods=['POST'])
@jwt_required()
def add_groupe():
    """Permet d'ajouter un groupe via la route /groupe/add

    :raises ActionImpossibleException: Impossible d'ajouter le groupe spécifié dans la table groupe
    :raises DonneeExistanteException: Si un groupe présent dans la bdd possède le même que celui spécifier

    :return: l'id du groupe créé
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    query_start = "Insert into edt.groupe (Nom, AnneeScolaire, Annee"

    query_values = f"values ('{json_datas['Nom']}', '{json_datas['AnneeScolaire']}', '{json_datas['Annee']}'"
    if "idGroupe_parent" in json_datas.keys() and json_datas['idGroupe_parent'] != -1 : 

        query_start += ", idGroupe_parent"
        query_values += f", {json_data['idGroupe_parent']}"
    query_start += ") "
    query_values += ") returning idGroupe"
    query = query_start + query_values
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idGroupe = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_data['Nom'], "Nom", "groupe"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("groupe"))}), 500

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

    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    conn = connect_pg.connect()
    query = f"DELETE from edt.groupe WHERE idgroupe={idGroupe}"
    query2 = f"DELETE from edt.etudier WHERE idgroupe={idGroupe}"
    query3 = f"DELETE from edt.eleve WHERE idgroupe={idGroupe}"
    try:
        returnStatement = connect_pg.execute_commands(conn, query3)
        returnStatement = connect_pg.execute_commands(conn, query2)
        returnStatement = connect_pg.execute_commands(conn, query)
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "supprimer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(
        {"success": f"The group with id {idGroupe} and all subgroups from this group were successfully removed"}), 200


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
    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    key = ["Nom", "AnneeScolaire", "Annee", "idGroupe_parent"]
    for k in json_data.keys():
        if k not in key:
            return jsonify({'error': "missing or invalid key"}), 400
    req = "UPDATE edt.groupe SET "
    for k in json_data.keys():
        req += f"{k}='{json_data[k]}', "

    if req[-2:] == ", ":
        req = req[:-2]
    req += f" WHERE idGroupe={idGroupe} RETURNING *"

    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, req)
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "mettre à jour"))}), 500
    connect_pg.disconnect(conn)
    return jsonify({"success": f"the group with id {idGroupe} was successfully updated"}), 200


@groupe.route('/groupe/getCoursGroupe/<idGroupe>', methods=['GET'])
@jwt_required()
def get_cours_groupe(idGroupe):
    """Renvoit tous les cours du groupe spécifié par son idGroupe via la route /groupe/parent/get/<idGroupe>

    :param idGroupe: l'id d'un groupe présent dans la base de donnée
    :type idGroupe: str

    :raises DonneeIntrouvableException: Impossible de trouver le groupe spécifié dans la table groupe

    :return:  la liste des cours du groupe a qui appartient cet id
    :rtype: json
    """
    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    query = f"select edt.cours.* from edt.groupe inner join edt.etudier using(idGroupe) inner join edt.cours using(idCours) where idGroupe={idGroupe}"

    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("etudier"))}), 404
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
