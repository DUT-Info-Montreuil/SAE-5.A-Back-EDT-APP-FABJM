from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.salle_service import get_salle_statement
from src.services.equipement_service import get_equipement_statement

import src.services.permision as perm
import src.services.verification as verif 

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import datetime
salle = Blueprint('salle', __name__)

# TODO: Update salle

@salle.route('/salle/getDispo', methods=['GET', 'POST'])
@jwt_required()
def get_salle_dispo():
    """Renvoit toutes les salles disponible sur une période via la route /salle/getDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la période au format TIME(hh:mm:ss) spécifié dans le body
    :type NombreHeure: int

    :param Jour: date de la journée où la disponibilité des salles doit être vérifer au format DATE(yyyy-mm-dd)
    :type Jour: str

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table groupe, etudier ou cours
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreInvalideException: Si un des paramètres est invalide
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: toutes les salles disponibles
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
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = int(HeureDebut[6:8]))
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]))
    HeureFin = HeureDebut + NombreHeure

    heure_ouverture_iut = datetime.timedelta(hours = 8)
    heure_fermeture_iut = datetime.timedelta(hours = 19)

    if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé durant la période spécifié"))}), 404

    query = f""" select edt.salle.* from edt.salle full join edt.accuellir using(idSalle) full join edt.cours
    using(idCours) where (idSalle is not null) and ( '{json_datas['HeureDebut']}' <  HeureDebut 
    and  '{str(HeureFin)}' <= HeureDebut or '{json_datas['HeureDebut']}'::time >=  (HeureDebut + NombreHeure::interval))  
    or (HeureDebut is null) order by idSalle asc
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
        return jsonify({'error': str(apiException.ActionImpossibleException("Salle, Etudier ou Cours", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@salle.route('/salle/getAll', methods=['GET'])
@jwt_required()
def get_salle():
    """Renvoit toutes les salles via la route /salle/getAll

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table salle
    
    :return: toutes les salles
    :rtype: json
    """
    query = "SELECT * from edt.salle order by idsalle asc"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("salle"))}), 404
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
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
    if (not idSalle.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    

    query = f"SELECT * from edt.salle where idSalle='{idSalle}'"

    conn = connect_pg.connect()
    
    returnStatement = {}
    if not idSalle.isdigit() or type(idSalle) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("salle", idSalle))}), 404
        returnStatement = get_salle_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
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
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    query = f"select edt.salle.* from edt.salle inner join edt.accuellir  using(idSalle) inner join edt.cours using(idCours) where idCours={idCours} "
    returnStatement = []
    conn = connect_pg.connect()
    try:
        rows = connect_pg.get_query(conn, query)
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("accuellir", "récuperer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@salle.route('/salle/delete/<idSalle>', methods=['DELETE'])
@jwt_required()
def delete_salle(idSalle):
    """Permet de supprimer une salle via la route /salle/delete/<idSalle>
    
    :param idSalle: id de la salle à supprimer
    :type idSalle: int

    :raises ActionImpossibleException: Impossible de supprimer la salle spécifié dans la table salle
    
    :return: message de succès
    :rtype: str
    """
    if (not idSalle.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    
    query = f"delete from edt.salle where idSalle={idSalle}"
    query2 = f"delete from edt.accuellir where idSalle={idSalle}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query2)
        returnStatement = connect_pg.execute_commands(conn, query)
        
    except(Exception) as e:
        print(e)
        return jsonify({'error': str(apiException.ActionImpossibleException("salle","supprimé"))}), 500
    
    return jsonify({'success': 'salle supprimé'}), 200

@salle.route('/salle/add', methods=['POST'])
@jwt_required()
def add_salle():
    """Permet d'ajouter une salle via la route /salle/add
    
    :param salle: salle à ajouter, spécifié dans le body
    :type salle: json

    :raises ActionImpossibleException: Impossible d'ajouter la salle spécifié dans la table salle
    :raises DonneeExistanteException: Cette salle existe déjà
    
    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    print(json_data)
    query = f"Insert into edt.salle (Nom, Capacite) values ('{json_data['Nom']}',{json_data['Capacite']}) returning idSalle"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except Exception as e:
        print(e)
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_data['Nom'], "Nom", "salle"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("salle"))}), 500

    return jsonify({"success" : "la salle a été ajouté" , "idSalle" : returnStatement }), 200



##################    Equipement de Salle    ####################
# TODO: Delete
@salle.route('/salle/get/equipement/<idSalle>', methods=['GET'])
@jwt_required()
def get_equipements_of_salle(idSalle):
    """Renvoit tous les salles au quel l'equipement(avec l'idEquipement) est lié via la route /salle/get/equipement/<idSalle>

    :param idSalle: l'id d'un groupe présent dans la base de donnée
    :type idSalle: str

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route
    
    :return: tous les equipements d'une salle
    :rtype: json
    """
    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)

    if(permision == 3):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"SELECT equipement.* from edt.equiper AS e NATURAL JOIN edt.equipement AS equipement WHERE e.idSalle={idSalle}"

    
    returnStatement = []
    try:
        equipements = connect_pg.get_query(conn, query)
        if equipements == []:
            return jsonify([])
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except(Exception) as e:
        print(e)
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
    
   

@salle.route('/salle/add/equipement/<idSalle>', methods=['POST'])
@jwt_required()
def add_equipements_of_salle(idSalle):
    """Permet d'ajouter une ou plusieurs salles a un équipement via la route /equipement/add/salle/<idEquipement>

    :param idSalle: l'id d'un groupe présent dans la base de donnée
    :type idSalle: str

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route

    :return: un tableau d'id d'equipement crééent
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400

    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)

    if not (perm.permissionCheck(get_jwt_identity(), 0 , conn)):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403
    query = "INSERT INTO edt.equiper (idSalle, idEquipement) VALUES "
    value_query = []

    for data in json_data['idEquipement']:
        value_query.append(f"({idSalle},'{data}')")

    query += ",".join(value_query) + " returning idEquipement"

    # TODO: find why only one id is return when multiple one are inserted
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    # TODO: handle error pair of key already exist
    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipements with the ids {returnStatement} were successfully created"}), 200    #{', '.join(tabIdEquipement)}







@salle.route('/salle/update', methods=['PUT'])
@jwt_required()
def update_salle():
    """Permet de modifier une salle via la route /salle/update
    
    :param salle: salle à modifier, spécifié dans le body
    :type salle: json

    :raises InsertionImpossibleException: Impossible de modifier la salle spécifié dans la table salle
    
    :return: message de succès
    :rtype: str
    """
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    query = f"update edt.salle set Numero='{json_datas['Numero']}', Capacite={json_datas['Capacite']} where idSalle={json_datas['idSalle']}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("salle"))}), 500
    return jsonify({'success': 'salle modifié'}), 200

