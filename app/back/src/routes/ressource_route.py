from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException


from src.config import config
from src.services.ressource_service import get_ressource_statement
import src.services.permision as perm

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

ressource = Blueprint('ressource', __name__)





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
    :raises InsertionImpossibleException: Impossible de réaliser l'insertion

    :return: id de la ressource
    :rtype: int
    """
    json_datas = request.get_json()
    if (not idRessource.isdigit() or type(json_datas['idProf']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idRessource ou idProf", "numérique"))}), 400
    
    
    if 'idProf' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    returnStatement = {}
    query = f"Insert into edt.responsable (idProf, idRessource) values ('{json_datas['idProf']}', '{idRessource}') returning idRessource"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "prof" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Professeur ", json_datas['idProf']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idRessource))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idRessource = {idRessource} et idProf = {json_datas['idProf']}"
            messageColonne = f"idRessource et idProf"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "responsable"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("responsable"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


def getEnseignantRessource(idUtilisateur , conn):
    """ Renvoie les ressources au quelle enseigne un professeur
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les ressources
    :rtype: list
    """
    idProf = connect_pg.get_query(conn , f"SELECT idProf FROM edt.professeur WHERE idutilisateur ={idUtilisateur}")[0][0]
    result = connect_pg.get_query(conn , f"Select edt.ressource.* from edt.ressource inner join edt.responsable as r1 using(idRessource)  where r1.idProf = {idProf} order by idRessource asc")
    
    return result

def getEleveRessource(idUtilisateur , conn):
    """ Renvoie les ressources qu'un élève étudie
    
    :param idUtilisateur: idUtilisateur du professeur
    :type idUtilisateur: int
    
    :param conn: la connection à une base de donnée
    :type conn: une classe heritant de la classe mère Connexion

    :return: retourne les ressources
    :rtype: list
    """
    result = connect_pg.get_query(conn , f"Select edt.ressource.* from edt.ressource inner join edt.cours using(idRessource) inner join edt.etudier using(idCours) inner join edt.eleve as e1 using(idGroupe) where e1.idutilisateur ={idUtilisateur} order by idRessource asc")
    
    return result

@ressource.route('/ressource/getAll')
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
    

    query = "select * from edt.ressource order by idressource asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@ressource.route('/ressource/getDispo')
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
    

    query = "select * from edt.ressource where NbrHeureSemestre > '00:00' order by idRessource asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
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

    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    if("Titre" not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Titre"))}), 400
    if('NbrHeureSemestre' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("NbrHeureSemestre"))}), 400
    if('CodeCouleur' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("CodeCouleur"))}), 400
    if('IdSemestre' not in json_datas.keys()):
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("IdSemestre"))}), 400
    if "Numero" not in json_datas.keys():
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException("Numero"))}), 400
    query = f"Insert into edt.ressource (titre, nbrheuresemestre, codecouleur, idsemestre , numero) values ('{json_datas['Titre']}', '{json_datas['NbrHeureSemestre']}', '{json_datas['CodeCouleur']}', '{json_datas['IdSemestre']}' , '{json_datas['Numero']}') returning idressource"
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
    
    query = f"select * from edt.ressource where idressource = {id}"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_ressource_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("ressource"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@ressource.route('/ressource/update/<id>', methods=['PUT','GET'])
@jwt_required()
def UpdateRessource(id) :
    """Permet de mettre à jour une ressource spécifié par son id via la route /ressource/update/<id>
    
    :param id: id de la ressource à modifier
    :type id: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table ressource
    :raises ParamètreBodyManquantException: Si le body est manquant
    :raises ParamètreInvalideException: Si un paramètre est invalide
    
    :return:  la ressource a qui appartient cette userNidame
    :rtype: json
    """
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 1 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
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
    req += f" WHERE idressource = {id}"
    
    con = connect_pg.connect()
    try:
        connect_pg.execute_commands(con, req)
    except Exception as e:
        return jsonify({'error': e}), 500
    
    return jsonify({'success': 'ressource updated'}), 200 