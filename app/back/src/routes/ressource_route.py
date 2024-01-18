from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException


from src.config import config
from src.services.ressource_service import *
from src.routes.cours_route import supprimer_cours
import src.services.permision as perm

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

ressource = Blueprint('ressource', __name__)


# TODO: refactor and add method


@ressource.route('/ressource/attribuerResponsable/<idRessource>', methods=['POST', 'PUT'])
@jwt_required()
def attribuerResponsable(idRessource):
    """Permet d'attribuer une salle à un ressource via la route /ressource/attribuerResponsable
    
    :param idRessource: id du ressource qui doit recevoir une salle
    :type idRessource: int

    :param idProf: id du professeur responsable de la ressource spécifié dans le body
    :type idProf: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idRessource est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser l'insertion

    :return: id de la ressource
    :rtype: int
    """
    json_data = request.get_json()
    if (not idRessource.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idRessource", "numérique"))}), 400
    
    
    if 'idProf' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if type(json_data['idProf']) != int:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    returnStatement = {}
    query = f"Insert into edt.responsable (idProf, idRessource) values ('{json_data['idProf']}', '{idRessource}') returning idRessource"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "prof" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Professeur ", json_data['idProf']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressource ", idRessource))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idRessource = {idRessource} et idProf = {json_data['idProf']}"
            messageColonne = f"idRessource et idProf"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "responsable"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("responsable"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@ressource.route('/ressource/getResponsable/<idRessource>', methods=['GET','POST'])
@jwt_required()
def get_responsable(idRessource):
    """Renvoit le responsable de la ressource via la route /ressource/getResponsable/<idRessource>
    
    :param idRessource: id de la ressouce 
    :type idRessource: int
    
    :raises ParamètreTypeInvalideException: Le type de idRessource est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """

    if (not idRessource.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idRessource", "numérique"))}), 400
    

    query = f"Select edt.professeur.* from edt.professeur inner join edt.responsable  using(idProf)  inner join edt.ressource as e1 using (idRessource) where e1.idRessource = {idRessource} order by idProf asc"
    returnStatement = []
    conn = connect_pg.connect()
    
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Responsable"))}), 400
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Responsable", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
# TODO: reparer fonction
@ressource.route('/ressource/supprimerResponsable/<idRessource>', methods=['DELETE'])
@jwt_required()
def supprimer_responsable(idRessource):
    """Permet de supprimer un responsable assigner à une ressouces via la route /ressource/supprimerResponsable/<idRessource>
    
    :param idRessource: id de la ressources
    :type idRessource: int

    :param idProf: id du professeur à supprimer spécifié dans le body
    :type idProf: int

    :raises ParamètreTypeInvalideException: Si le type de idRessource est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si la clée idRessource ou idProf n'a pas pu être trouvé
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de l'insertion

    :return: id de la ressource
    :rtype: json
    """
    json_data = request.get_json()
    if (not idRessource.isdigit() ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idRessource", "numérique"))}), 400

    
    
    if 'idProf' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if type(json_data['idProf']) != int:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    query = f"delete from edt.responsable where idRessource={idRessource} and idProf = {json_data['idProf']}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "prof" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Professeur ", json_data['idProf']))}), 400

            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressource ", idRessource))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("responsable", "supprimer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(idRessource)



@ressource.route('/ressource/getAll', methods=['GET'])
@jwt_required()
def getAll_ressource():
    """Renvoit toutes les ressources via la route /ressource/getAll

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table ressource
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table ressource
    
    :return:  toutes les resources
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403

    if(perm.getUserPermission(get_jwt_identity() , conn)[0] == 2):
        
        returnStatement = []
        try:
            cours = getRessourceProf(get_jwt_identity() , conn)
            if cours == []:
                return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
            for row in cours:
                returnStatement.append(get_ressource_statement(row))
        except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récuperer"))}), 500
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    
    elif(perm.getUserPermission(get_jwt_identity() , conn)[0] == 3):
        
        returnStatement = []
        try:
            cours = getRessourceEleve(get_jwt_identity() , conn)
            if cours == []:
                return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
            for row in cours:
                returnStatement.append(get_ressource_statement(row))
        except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récuperer"))}), 500
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    

    query = "SELECT * from edt.ressource order by idressource asc"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@ressource.route('/ressource/getDispo', methods=['GET'])
@jwt_required()
def get_ressource_dispo():
    """Renvoit toutes les ressources disponible, c'est à dire celles dont toutes les heures n'ont pas encore été allouées via la route /ressource/getDispo

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table ressource
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table ressource
    
    :return:  toutes les resources
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    

    query = "select * from edt.ressource where NbrHeureSemestre > 0 order by idRessource asc"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@ressource.route('/ressource/add', methods=['POST'])
@jwt_required()
def addRessource() : 
    
    """Ajoute une ressource via la route /ressource/add

    :param Titre: titre de la ressource spécifié dans le body
    :type Titre: str

    :param NbrHeureSemestre: nombre d'heure de la ressource spécifié dans le body
    :type NbrHeureSemestre: int

    :param CodeCouleur: code couleur de la ressource spécifié dans le body
    :type CodeCouleur: str

    :param IdSemestre: id du semestre de la ressource spécifié dans le body
    :type IdSemestre: int

    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises ParamètreBodyManquantException: Si le body n'a pas pu être trouvé ou un paramètre est manquant dans le body

    :return:  ressource ajouté
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    if("Titre" not in json_data.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Titre"))}), 400
    if('NbrHeureSemestre' not in json_data.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("NbrHeureSemestre"))}), 400
    if('CodeCouleur' not in json_data.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("CodeCouleur"))}), 400
    if('IdSemestre' not in json_data.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("IdSemestre"))}), 400
    if "Numero" not in json_data.keys():
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Numero"))}), 400
    query = f"Insert into edt.ressource (titre, nbrheuresemestre, codecouleur, idsemestre , numero) values ('{json_data['Titre']}', '{json_data['NbrHeureSemestre']}', '{json_data['CodeCouleur']}', '{json_data['IdSemestre']}' , '{json_data['Numero']}') returning idressource"
    conn = connect_pg.connect()
    try  :
        connect_pg.execute_commands(conn, query)
    except Exception as e: 
        return jsonify({'error': e}), 500
    connect_pg.disconnect(conn)
    return jsonify({'success': 'ressource added'}), 200


@ressource.route('/ressource/get/<id>', methods=['GET'])
@jwt_required()
def getRessource(id):
    """Renvoit une ressource spécifié par son id via la route /ressource/get/<id>
    
    :param id: id d'une ressource
    :type id: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table ressource
    
    :return:  la ressource a qui appartient cette userNidame
    :rtype: json
    """
    
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    if (not id.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("id", "numérique"))}), 400
    
    query = f"SELECT * from edt.ressource where idressource = {id}"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@ressource.route('/ressource/update/<idRessource>', methods=['PUT','GET'])
@jwt_required()
def UpdateRessource(idRessource) :
    """Permet de mettre à jour une ressource spécifié par son idRessource via la route /ressource/update/<idRessource>
    
    :param idRessource: idRessource de la ressource à modifier
    :type idRessource: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises ParamètreBodyManquantException: Si le body est manquant
    :raises ParamètreInvalideException: Si un paramètre est invalide
    
    :return:  la ressource a qui appartient cette userNidame
    :rtype: json
    """

    table_name = "Ressource"
    json_data = request.get_json()
    keys = ["Titre", "NbrHeureSemestre", "CodeCouleur", "IdSemestre", "Numero"]
    
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403

    if (not idRessource.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idRessource", "numérique"))}), 400
    
    datas = request.get_json()
    if not datas:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    key = ["Titre", "NbrHeureSemestre", "CodeCouleur", "IdSemestre", "Numero"]
    for k in datas.keys():
        if k not in key:
            return jsonify({'erreur': str(apiException.ParamètreInvalideException(k))}), 400
    req = "UPDATE edt.ressource SET "
    for key in datas.keys():
        
        req += f"{key} = '{datas[key]}', "    
    
    #remove last comma
    if req[-2:] == ", ":
        req = req[:-2]
    req += f" WHERE idressource = {idRessource}"
    
    con = connect_pg.connect()
    try:
        connect_pg.execute_commands(con, req)
    except Exception as e:
        return jsonify({'error': e}), 500
    
    return jsonify({'success': 'ressource updated'}), 200 



@ressource.route('/ressource/supprimer/<idRessource>', methods=['DELETE'])
@jwt_required()
def supprimer_ressource(idRessource):
    """Permet de supprimer une ressource via la route /ressource/supprimer/<idRessource>
    
    :param idRessource: id du cours à supprimer
    :type idRessource: int

    :raises ParamètreTypeInvalideException: Le type de idRessource est invalide, une valeur numérique est attendue

    :return: id du cours supprimer si présent
    :rtype: json
    """
    

    if (not idRessource.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    conn = connect_pg.connect()

    query = f"select idCours from edt.cours where idRessource={idRessource}"

    try:
        returnStatement = connect_pg.get_query(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours","récupérer"))}), 500
    
    for k in range(len(returnStatement)):
        for i in range(len(returnStatement[k])):
            supprimer_cours(str(returnStatement[k][i]))

    
    query = f"delete  from edt.ressource where idRessource={idRessource}"
    query2 = f"delete  from edt.responsable where idRessource={idRessource}"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query2)
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("ressource","supprimé"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(idRessource)

