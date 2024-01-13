from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.cours_service import get_cours_statement, getProfCours, getEleveCours

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error
import src.services.permision as perm

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
cours = Blueprint('cours', __name__)



@cours.route('/cours/getAll')
@jwt_required()
def getAll_cours():
    """Renvoit toutes les cours via la route /cours/getAll

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table cours
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table cours
    
    :return: toutes les cours
    :rtype: json
    """
    conn = connect_pg.connect()
    
    query = "select * from edt.cours order by idCours asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/get', methods=['GET','POST'])
@jwt_required()
def get_cours():
    """Renvoit les cours spécifique à un utilisateur si possible sinon renvoit les cours générale via la route /cours/get
    
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé correspont aux critère
    
    :return: Les cours 
    :rtype: json
    """

    conn = connect_pg.connect()
    if(perm.getUserPermission(get_jwt_identity() , conn) == 2):
        cours = getProfCours(get_jwt_identity() , conn)
        returnStatement = []
        try:
            for row in cours:
                returnStatement.append(get_cours_statement(row))
        except(TypeError) as e:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    
    elif(perm.getUserPermission(get_jwt_identity() , conn) == 3):
        cours = getEleveCours(get_jwt_identity() , conn)
        returnStatement = []
        try:
            for row in cours:
                returnStatement.append(get_cours_statement(row))
        except(TypeError) as e:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    
    else :
        query = f"select * from edt.cours order by idCours"
        returnStatement = []
        try:
            rows = connect_pg.get_query(conn, query)
            if rows == []:
                return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
            for row in rows:
                returnStatement.append(get_cours_statement(row))
        except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)




@cours.route('/cours/getCoursSemestre/<idSemestre>', methods=['GET','POST'])
@jwt_required()
def get_cours_semestre(idSemestre):
    """Renvoit toutes les cours d'un semestre via la route /cours/getCoursSemestre/<idSemestre>

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table cours
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table cours
    
    :return: toutes les cours d'un semestre
    :rtype: json
    """
    conn = connect_pg.connect()
    
    query = f"select edt.cours.* from edt.cours inner join edt.ressource using(idRessource) inner join edt.semestre using(idSemestre) where idSemestre = {idSemestre} order by idCours"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/deplacer/<idCours>', methods=['PUT'])
@jwt_required()
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
    # TODO: refactor
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


@cours.route('/cours/attribuerSalle/<idCours>', methods=['POST', 'PUT'])
@jwt_required()
def attribuerSalle(idCours):
    """Permet d'attribuer une salle à un cours via la route /cours/attribuerSalle/<idCours>
    
    :param idCours: id du cours qui doit recevoir une salle
    :type idCours: int

    :param idSalle: id de la salle à attribuer
    :type idSalle: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser l'insertion

    :return: id du cours supprimer si présent
    :rtype: json
    """
    json_datas = request.get_json()
    if (not idCours.isdigit() or type(json_datas['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idSalle", "numérique"))}), 400
    
    
    if 'idSalle' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    returnStatement = {}
    query = f"Insert into edt.accuellir (idSalle, idCours) values ('{json_datas['idSalle']}', '{idCours}') returning idCours"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "salle" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Salle ", json_datas['idSalle']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idCours = {idCours} et idSalle = {json_datas['idSalle']}"
            messageColonne = f"idCours et idSalle"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "accuellir"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("accuellir"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/changerSalle/<idCours>', methods=['PUT'])
@jwt_required()
def changer_salle(idCours):
    """Permet de changer la salle attribuer à un cours via la route /cours/changerSalle/<idCours>
    
    :param idCours: id du cours dont la salle doit être changer
    :type idCours: int

    :param idSalle: id de la salle de la nouvelle salle
    :type idSalle: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises DonneeIntrouvableException: Une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser la mise à jour

    :return: id du cours dont la salle à changer
    :rtype: json
    """
    json_datas = request.get_json()
    if (not idCours.isdigit() or type(json_datas['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idSalle", "numérique"))}), 400
    else:
        query = f"update edt.accuellir set idSalle = {json_datas['idSalle']}  where idCours={idCours}"
        conn = connect_pg.connect()
        
        try:
            connect_pg.execute_commands(conn, query)
        except Exception as e:
            if e.pgcode == "23503":# violation contrainte clée étrangère
                if "salle" in str(e):
                    return jsonify({'error': str(apiException.DonneeIntrouvableException("Salle ", json_datas['idSalle']))}), 400
                else:
                    return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
            elif e.pgcode == "23505": # si existe déjà
                messageId = f"idCours = {idCours} et idSalle = {json_datas['idSalle']}"
                messageColonne = f"idCours et idSalle"
                return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "accuellir"))}), 400
            
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.ActionImpossibleException("accuellir", "mise à jour"))}), 500
        
        connect_pg.disconnect(conn)
        return jsonify(idCours)

@cours.route('/cours/supprimerSalle/<idCours>', methods=['DELETE'])
@jwt_required()
def supprimer_salle(idCours):
    """Permet de supprimer une salle attribuer à un cours via la route /cours/supprimerSalle/<idCours>
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours supprimer si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    else:
        query = "delete from edt.accuellir where idCours=%(idCours)s" % {'idCours':idCours}
        conn = connect_pg.connect()
        connect_pg.execute_commands(conn, query)
        connect_pg.disconnect(conn)
        return jsonify(idCours)


@cours.route('/cours/delete/<idCours>', methods=['DELETE'])
@jwt_required()
def delete_cours(idCours):
    """Permet de supprimer un cours via la route /cours/delete/<idCours>
    
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
@jwt_required()
def add_cours():
    """Permet d'ajouter un cours via la route /cours/add
    
    :param cours: donnée représentant un cours spécifié dans le body
    :type cours: json
    
    :raises ActionImpossibleException: Impossible d'ajouter le cours spécifié dans la table cours
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
            return jsonify({'error': str(apiException.ActionImpossibleException("cours"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)



@cours.route('/cours/getCoursSalle/<idSalle>', methods=['GET','POST'])
@jwt_required()
def get_cours_salle(idSalle):
    """Renvoit les se déroulant dans une salle via la route /cours/getCoursSalle/<idSalle>
    
    :param idSalle: id du cours à rechercher
    :type idSalle: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur survient durant la récupération des données
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """
    query = f"Select edt.cours.* from edt.cours inner join edt.accuellir  using(idCours)  inner join edt.salle as e1 using (idSalle) where e1.idSalle = {idSalle} order by idCours asc"
    returnStatement = []
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    if rows == []:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("Accuellir"))}), 400
    try:
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Accuellir", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)