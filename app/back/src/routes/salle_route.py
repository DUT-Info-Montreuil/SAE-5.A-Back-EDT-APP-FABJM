from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.salle_service import get_salle_statement
import src.services.verification as verif 

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import datetime
salle = Blueprint('salle', __name__)


@salle.route('/salle/getDispo', methods=['GET', 'POST'])
@jwt_required()
def get_salle_dispo():
    """Renvoit toutes les salles disponible sur une période via la route /salle/getDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la période spécifié dans le body
    :type NombreHeure: int

    :param Jour: date de la journée où la disponibilité des cours doit être vérifer au format TIMESTAMP(yyyy:mm:jj)
    :type Jour: str

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table groupe, etudier ou cours
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreInvalideException: Si un des paramètres est invalide
    :raises InsertionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: toutes les salles disponibles
    :rtype: flask.wrappers.Response(json)
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    
    if 'HeureDebut' not in json_datas or 'Jour' not in json_datas or 'NombreHeure' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if not verif.estDeTypeTime(json_datas['HeureDebut']) or not verif.estDeTypeTimeStamp(json_datas['Jour']) or not type(json_datas['NombreHeure']) == int:
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure ou Jour"))}), 404

    HeureDebut = json_datas['HeureDebut']
    NombreHeure = json_datas['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = int(HeureDebut[6:8]))
    NombreHeure = datetime.timedelta(hours = NombreHeure)
    HeureFin = HeureDebut + NombreHeure

    heure_ouverture_iut = datetime.timedelta(hours = 8)
    heure_fermeture_iut = datetime.timedelta(hours = 19)

    if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé durant la période spécifié"))}), 404

    query = f""" select edt.salle.* from edt.salle full join edt.accuellir using(idSalle) full join edt.cours
    using(idCours) where (idSalle is not null) and ( '{json_datas['HeureDebut']}' <  HeureDebut 
    and  '{str(HeureFin)}' <= HeureDebut or '{json_datas['HeureDebut']}' >=  (HeureDebut + NombreHeure * interval '1 hours')) or (HeureDebut is null) order by idsalle asc
    """
    conn = connect_pg.connect()
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Aucune salle disponible n'a été trouvé l'horaire spécifié"))}), 400
        
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except Exception as e:
        print(e)
        return jsonify({'error': str(apiException.InsertionImpossibleException("Salle, Etudier ou Cours", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@salle.route('/salle/getAll')
@jwt_required()
def get_salle():
    """Renvoit toutes les salles via la route /salle/getAll

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table salle
    
    :return: toutes les salles
    :rtype: json
    """
    query = "select * from edt.salle order by idsalle asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except TypeError as e:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("salle"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@salle.route('/salle/get/<idSalle>', methods=['GET', 'POST'])
@jwt_required()
def get_one_salle(idSalle):
    """Renvoit une salle spécifié par son id via la route /salle/get<idSalle>

    :param idSalle: id d'une salle présent dans la base de donnée
    :type idSalle: int

    :raises DonneeIntrouvableException: Impossible de trouver la salle spécifié dans la table salle
    :raises ParamètreTypeInvalideException: Le type de l'id salle est invalide, une valeur numérique est attendue

    :return: la salle qui correspond à l'id du numéro entré en paramètre
    :rtype: json
    """

    query = f"select * from edt.salle where idSalle='{idSalle}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if not idSalle.isdigit() or type(idSalle) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_salle_statement(rows[0])
    except TypeError as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("salle", idSalle))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200

@salle.route('/salle/getSalleCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_salle_cours(idCours):
    """Renvoit la salle dans lequel se déroule le cours via la route /cours/getSalle/<idCours>
    
    :param idCours: id du cours à rechercher
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """
    query = f"select edt.salle.* from edt.salle inner join edt.accuellir  using(idSalle) inner join edt.cours using(idCours) where idCours={idCours} "
    returnStatement = []
    conn = connect_pg.connect()
    try:
        rows = connect_pg.get_query(conn, query)
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except IndexError:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("Accuellir", idCours))}), 400
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@salle.route('/salle/delete/<idSalle>', methods=['DELETE'])
@jwt_required()
def delete_salle(idSalle):
    """Permet de supprimer une salle via la route /salle/delete/<idSalle>
    
    :param idSalle: id de la salle à supprimer
    :type idSalle: int

    :raises InsertionImpossibleException: Impossible de supprimer la salle spécifié dans la table salle
    
    :return: message de succès
    :rtype: str
    """
    query = f"delete from edt.salle where idSalle={idSalle}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("salle","supprimé"))}), 500
    
    return jsonify({'success': 'salle supprimé'}), 200

@salle.route('/salle/add', methods=['POST'])
@jwt_required()
def add_salle():
    """Permet d'ajouter une salle via la route /salle/add
    
    :param salle: salle à ajouter, spécifié dans le body
    :type salle: json

    :raises InsertionImpossibleException: Impossible d'ajouter la salle spécifié dans la table salle
    :raises DonneeExistanteException: Cette salle existe déjà
    
    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400

    query = f"Insert into edt.salle (Numero, Capacite) values ('{json_datas['Numero']}',{json_datas['Capacite']}) returning idSalle"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_datas['Numero'], "Numero", "salle"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("salle"))}), 500

    return jsonify({"success" : "la salle a été ajouté"}), 200