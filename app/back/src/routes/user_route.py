import base64
from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.user_service import *
import src.services.permision as perm
import src.utilitary as util
import src.services.verification as verif
from src.services.user_service import get_professeur_statement

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import json
import datetime
user = Blueprint('user', __name__)

# TODO: refactor user

@user.route('/utilisateurs/getProfDispo', methods=['GET', 'POST'])
@jwt_required()
def get_prof_dispo():
    """Renvoit tous les professeurs disponible sur une période via la route /utilisateurs/getProfDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la périodeau format TIME(hh:mm:ss) à spécifié dans le body
    :type NombreHeure: int

    :param Jour: date de la journée où la disponibilité des professeurs doit être vérifer au format DATE(yyyy-mm-dd)
    :type Jour: str

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table groupe, etudier ou cours
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreInvalideException: Si un des paramètres est invalide
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: touts les professeurs disponibles
    :rtype: flask.wrappers.Response(json)
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    
    if 'HeureDebut' not in json_data or 'Jour' not in json_data or 'NombreHeure' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if not verif.estDeTypeTime(json_data['HeureDebut']) or not verif.estDeTypeDate(json_data['Jour']) or not verif.estDeTypeTime(json_data['NombreHeure']):
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure ou Jour"))}), 404
    
    heureDebut_str = json_data['HeureDebut']  
    nombreHeure_str = json_data['NombreHeure'] 
    jour_str = json_data['Jour'] 
    
    profs = []
    heureDebut = datetime.datetime.strptime(heureDebut_str, '%H:%M:%S').time()
    nombreHeure = datetime.datetime.strptime(nombreHeure_str, '%H:%M:%S').time()
    jour = datetime.datetime.strptime(jour_str, '%Y-%m-%d').date()
    
    debut = datetime.datetime.combine(jour, heureDebut)
    fin = datetime.datetime.combine(jour, heureDebut) + datetime.timedelta(hours=nombreHeure.hour, minutes=nombreHeure.minute, seconds=nombreHeure.second)
       
    conn = connect_pg.connect()
    query = f"select * from edt.Professeur;"
    try:
        profs = connect_pg.get_query(conn, query)
    except:
        return jsonify({'error': str(apiException.ActionImpossibleException("Professeur", "récuperer"))}), 500
    
    rows = []
    query = f"select * from edt.Enseigner inner join edt.cours using(idcours) where edt.cours.jour = '{jour}';"
    try:
        rows = connect_pg.get_query(conn, query)
    except:
        return jsonify({'error': str(apiException.ActionImpossibleException("Enseigner", "récuperer"))}), 500
        
    returnStatement = []
    for prof in profs:
        is_dispo = True
        for row in rows:
            rowHeureDebut = row[2]
            nombreHeure = row[3]
            rowJour = row[4]
            rowDebut = datetime.datetime.combine(rowJour, rowHeureDebut)
            rowFin = datetime.datetime.combine(rowJour, rowHeureDebut) + datetime.timedelta(hours=nombreHeure.hour, minutes=nombreHeure.minute, seconds=nombreHeure.second)
            if prof[0] == row[1]:
                #if debut is between rowDebut and rowFin or if fin is between rowDebut and rowFin
                if ((debut > rowDebut and debut < rowFin) or (fin > rowDebut and fin < rowFin)):
                    print('prof non dispo : ', prof)
                    is_dispo = False
                    
                elif ((rowDebut > debut and rowDebut < fin) or (rowFin > debut and rowFin < fin)):
                    print('prof non dispo : ', prof)
                    is_dispo = False

        if is_dispo:
            returnStatement.append(get_professeur_statement(prof))
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200



@user.route('/utilisateurs/getAll', methods=['GET','POST'])
@jwt_required()
def get_utilisateur():
    """Renvoit tous les utilisateurs via la route /utilisateurs/getAll

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table utilisateur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table utilisateur
    
    :return:  tous les utilisateurs
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    query = util.get("Utilisateur", key_to_return=["idUtilisateur", "FirstName", "LastName", "Username", "FirstLogin"])
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify([])
        for row in rows:
            p = perm.getUserPermission(row[0] , conn)
            returnStatement.append(get_utilisateur_statement(row, p[0]))
    except(TypeError) as e:
        return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)



@user.route('/utilisateurs/getProfE', methods=['GET','POST'])
@jwt_required()
def get_prof_etendue():
    """Renvoit tous les professeurs avec des informations de la table utilisateur via la route /utilisateurs/getProfE

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table prof/utilisateur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table utilisateur/prof
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return:  tous les utilisateurs
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()

    query = "select idprof,initiale, idsalle,firstname, lastname,idutilisateur from edt.utilisateur inner join edt.professeur using(idutilisateur) order by IdUtilisateur asc"
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("professeur"))}), 404
        for row in rows:
                returnStatement.append(get_professeur_statement_extended(row))
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getAllProf', methods=['GET'])
@jwt_required()
def get_prof():
    """Renvoit tous les profs via la route /utilisateurs/getAllProf

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return:  tous les professeurs
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()

    query = "select * from edt.professeur order by IdUtilisateur asc"
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("professeur"))}), 404
        for row in rows:
                returnStatement.append(get_professeur_statement(row))
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getProfHeureTravailler/<idProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_heure_travailler(idProf):
    """Renvoit toutes les heures faites par un prof via la route /utilisateurs/getProfHeureTravailler/<idProf>

    :param idProf: id d'un professeur présent dans la base de donnée
    :type idProf: int

    :param pasSae: boolean pour savoir si les sae doivent être prise en compte spécifié via le body
    :type pasSae: bool(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return:  tous les professeurs
    :rtype: json
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()
    querySae = ""
    try:
        json_data = request.get_json()
        if 'pasSae' in json_data:
            if type(json_data['pasSae']) == bool:
                if json_data['pasSae']:
                    querySae += f" and (TypeCours != 'Sae') "
            else:
                return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "bool"))}), 400

    except(Exception) as e: # Si aucune pasSae n'es fournie
        pass

    dateAujourdhui = str(datetime.date.today())
    heureActuelle = str(datetime.datetime.now())

    query = f"""select sum(nombreheure) as nombreheureTravailler from edt.cours inner join edt.enseigner 
    using(idCours)  where idProf = {idProf} and ((jour < '{dateAujourdhui}') or (jour = '{dateAujourdhui}' 
    and (HeureDebut + NombreHeure::interval) < '{heureActuelle}'::time)){querySae}
    """
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        result = str(rows[0][0])
        if result == "None":
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
        
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(result)


@user.route('/utilisateurs/getProfHeurePrevue/<idProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_heure_prevue(idProf):
    """Renvoit toutes les heures faites par un prof via la route /utilisateurs/getProfHeurePrevue/<idProf>

    :param idProf: id d'un professeur présent dans la base de donnée
    :type idProf: int

    :param pasSae: boolean pour savoir si les sae doivent être prise en compte spécifié via le body
    :type pasSae: bool(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return:  tous les professeurs
    :rtype: json
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()
    querySae = ""
    try:
        json_data = request.get_json()
        if 'pasSae' in json_data:
            if type(json_data['pasSae']) == bool:
                if json_data['pasSae'] :
                    querySae += f" and (TypeCours != 'Sae') "
            else:
                return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "bool"))}), 400

    except(Exception) as e: # Si aucune pasSae n'es fournie
        pass

    dateAujourdhui = str(datetime.date.today())
    heureActuelle = str(datetime.datetime.now())

    query = f"""select sum(nombreheure) as nombreheureTravailler from edt.cours inner join edt.enseigner 
    using(idCours)  where idProf = {idProf} and ((jour > '{dateAujourdhui}') or (jour = '{dateAujourdhui}' 
    and (HeureDebut + NombreHeure::interval) > '{heureActuelle}'::time)){querySae};
    """
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        result = str(rows[0][0])
        if result == "None":
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
        
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(result)


@user.route('/utilisateurs/getTeacherHoursInMonth/<idProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_heure_travailler_mois(idProf):
    
    """Renvoie le nombre total d'heures travaillées par un professeur pour le mois spécifié, 
    incluant les heures travaillées jusqu'à la date actuelle, via la route /utilisateurs/getTeacherHoursInMonth/<idProf>

    :param idProf: id d'un professeur présent dans la base de donnée
    :type idProf: int

    :param mois: mois à calculer au format YYYY-MM (ex : 2023-12) à spécifié dans le body
    :type mois: str

    :param currentDay: jour actuel au format YYYY-MM-DD (ex : 2023-12-31) à spécifié dans le body
    :type currentDay: str(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer la requête
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    
    :return: le nombre d'heures travaillées par le professeur pour le mois spécifié
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()

    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    if 'mois' not in json_data:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    mois = json_data['mois']
    
    
    query = f"""
    SELECT SUM(nombreheure) AS workedHours
    FROM edt.cours
    INNER JOIN edt.enseigner ON edt.cours.idCours = edt.enseigner.idCours
    INNER JOIN edt.ressource ON edt.cours.idRessource = edt.ressource.idRessource
    WHERE idProf = {idProf}
    """

    timeLimit = None

    if 'currentDay' in json_data:
        timeLimit = f" AND Jour >= '{mois}-01' AND Jour <= '{json_data['currentDay']}';"
    else:
        timeLimit = f" AND Jour >= '{mois}-01' AND Jour <= '{mois}-31';"

    try:
        rows = connect_pg.get_query(conn, query + timeLimit)
        if not rows:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500

    totalHours = str(rows[0][0])[:-3]

    query = f"""
    SELECT SUM(nombreheure) AS workedHours
    FROM edt.cours inner join edt.enseigner on edt.cours.idCours = edt.enseigner.idCours
    where idProf = {idProf} and TypeCours = SAE"""

    try:
        rows = connect_pg.get_query(conn, query + timeLimit)
        if not rows:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404

    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500
    

    SAEHours = str(rows[0][0])[:-3]
    ppnTotalHours = rows[0][0]

    query = f"""
    SELECT SUM(nombreheure) AS workedHours
    FROM edt.cours inner join edt.enseigner on edt.cours.idCours = edt.enseigner.idCours
    where idProf = {idProf} and (TypeCours = TD or TypeCours = TP)"""

    try:
        rows = connect_pg.get_query(conn, query + timeLimit)
        if not rows:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500
    
    TDTPHours = str(rows[0][0])[:-3]
    ppnTotalHours += rows[0][0]

    query = f"""
    SELECT SUM(nombreheure) AS workedHours
    FROM edt.cours inner join edt.enseigner on edt.cours.idCours = edt.enseigner.idCours
    where idProf = {idProf} and TypeCours = AMPHI"""

    try:
        rows = connect_pg.get_query(conn, query + timeLimit)
        if not rows:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("cours", "récupérer"))}), 500
    
    AMPHIHours = str(rows[0][0])[:-3]
    ppnTotalHours += (rows[0][0] * 1.5)
    
    workedHours = {
        "total": totalHours,
        "SAE": SAEHours,
        "TDTP": TDTPHours,
        "AMPHI": AMPHIHours,
        "ppnTotal": str(ppnTotalHours)[:-3]
    }
    
    connect_pg.disconnect(conn)
    return jsonify(workedHours)


@user.route('/utilisateurs/getProfParInitiale/<initialeProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_par_initiale(initialeProf):
    """Renvoit un prof via ses initiales via la route /utilisateurs/getProfParInitiale/<initialeProf>

    :param initialeProf: initiale d'un professeur présent dans la base de donnée
    :type initialeProf: int

    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    :raises AucuneDonneeTrouverException: Une aucune donnée répondant aux critères n'a été trouvé dans la table professeur
    
    :return: un professeur
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    query = f"select * from edt.professeur where Initiale = '{initialeProf}'"
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("professeur",initialeProf))}), 404
        for row in rows:
            returnStatement.append(get_professeur_statement(row))
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getAllEnseignant', methods=['GET','POST'])
@jwt_required()
def get_enseignant():
    """Renvoit tous les enseignants via la route /utilisateurs/getAllEnseignant

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table enseigner
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table enseigner
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return:  tous les enseignants
    :rtype: json
    """
    
    conn = connect_pg.connect()
    query = "select distinct * from edt.enseigner order by idProf asc"
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("professeur"))}), 404
        for row in rows:
            returnStatement.append(json.loads((get_one_prof((row[0]))).data))
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getProf/<idProf>', methods=['GET','POST'])
@jwt_required()
def get_one_prof(idProf):
    """Renvoit un prof via son id via la route /utilisateurs/getProf/<idProf>

    :param idProf: id d'un professeur présent dans la base de donnée
    :type idProf: int

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un get dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée répondant aux critères n'a été trouvé dans la table professeur
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données

    :return: un professeur
    :rtype: json
    """
    
    conn = connect_pg.connect()

    query = f"select * from edt.professeur where idProf = {idProf} order by IdUtilisateur asc"
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("professeur",idProf))}), 404
        for row in rows:
            returnStatement.append(get_professeur_statement(row))
    except(Exception) as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getLoggedUser', methods=['GET'])
@jwt_required()
def get_logged_user():
    """Renvoit l'utilisateur connecté via la route /utilisateurs/getLoggedUser

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table utilisateurs
    
    
    :return:  l'utilisateur connecté
    :rtype: json
    """
    user_id = get_jwt_identity()
    conn = connect_pg.connect()
    
    querry = f"select idUtilisateur,FirstName,LastName,Username from edt.utilisateur where idutilisateur = {user_id}"

    user_rows = connect_pg.get_query(conn, querry)

    if not user_rows:
        connect_pg.disconnect(conn)
        return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 404
    
    user = get_utilisateur_protected_statement(user_rows[0])
    
    role_query = f"select IDAdmin from edt.admin where idUtilisateur = {user_id}"
    role_rows = connect_pg.get_query(conn, role_query)
    
    if role_rows:
        role = {
        "type": "0",
        "id": role_rows[0][0]
        }
        user["role"] = role
        connect_pg.disconnect(conn)
        return jsonify(user)
    
    role_query = f"SELECT p.idProf, p.initiale, s.nom FROM edt.professeur as p JOIN edt.salle as s ON p.idSalle = s.idSalle WHERE p.idUtilisateur = {user_id}"
    role_rows = connect_pg.get_query(conn, role_query)
    manager_query = f"SELECT * FROM edt.manager WHERE idProf = {role_rows[0][0]}"

    if not manager_query : 

        if role_rows:
            role = {
            "type": "2",
            "id": role_rows[0][0],
            "initiale": role_rows[0][1],
            "bureau": role_rows[0][2]
            }
            user["role"] = role
            connect_pg.disconnect(conn)
            return jsonify(user)
    else :
        if role_rows:
            role = {
            "type": "1",
            "id": role_rows[0][0],
            "initiale": role_rows[0][1],
            "bureau": role_rows[0][2]
            }
            user["role"] = role
            connect_pg.disconnect(conn)
            return jsonify(user)
    
    role_query = f"select idEleve,idGroupe  from edt.eleve where idUtilisateur = {user_id}"
    role_rows = connect_pg.get_query(conn, role_query)

    if role_rows:
        role = {
        "type": "3",
        "id": role_rows[0][0],
        "idGroupe": role_rows[0][1]
        }
        user["role"] = role
        connect_pg.disconnect(conn)
        return jsonify(user)
    
    return jsonify({'erreur': 'Rôle non trouvé'}), 404


@user.route('/utilisateurs/get/<userName>', methods=['GET','POST'])
@jwt_required()
def get_one_utilisateur(userName):
    """Renvoit un utilisateur spécifié par son userName via la route /utilisateurs/get<userName>
    
    :param userName: nom d'un utilisateur présent dans la base de donnée
    :type userName: str
    
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour récupérer les données présents dans la table utilisateurs
    :raises DonneeIntrouvableException: Impossible de trouver l'userName spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’userName est invalide, un string est attendue
    
    :return:  l'utilisateur a qui appartient cette userName
    :rtype: json
    """
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    (query, search_value) = util.get("Utilisateur", where={"Username":userName}, key_to_return=["idUtilisateur", "FirstName", "LastName", "Username", "FirstLogin"])

    conn = connect_pg.connect()
    
    returnStatement = {}
    if (userName.isdigit() or type(userName) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("userName", "string"))}), 400
    try:
        rows = connect_pg.get_query(conn, query, search_value)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", userName))}), 404
        returnStatement = get_utilisateur_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/add', methods=['POST'])
@jwt_required()
def add_utilisateur():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    
    :raises ActionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour créer un utlisateur
    
    :return: l'id de l'utilisateur crée
    :rtype: json

    """
    #{ "role": "eleve", "users": [ { "firstName": "Elève1", "lastName": "lastName", "info": { "idGroupe": "1", "idSalle": "", "isManager": "" } }, { "firstName": "Elève2", "lastName": "lastName", "info": { "idGroupe": "2", "idSalle": "", "isManager": "" } } ] } 
    
    #check if the user is admin
    conn = connect_pg.connect()
    json_data = request.get_json()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403

    # TODO: use nom salle in create user instead of id salle

    if not json_data:
            return jsonify({'error ': 'missing json body'}), 400
    
    if (json_data['role'] != "admin" and json_data['role'] != "professeur" and json_data['role'] != "eleve" and json_data['role'] != "manager"):
        return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    for user in json_data['users']:
        conn = connect_pg.connect()
        if "info" not in user.keys():
            return jsonify({'error': 'missing "info" part of the body'}), 400
        
        key = ["FirstName", "LastName", "Username", "Password"]
        for k in user.keys():
            if k in key:
                key.remove(k) 
        if len(key) != 0:
            return jsonify({'error ': 'missing ' + str(key)}), 400 
        
        user['Password'] = util.password_encode(user['Password'])
        
        query = f"Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{user['FirstName']}', '{user['LastName']}', '{user['Username']}', '{user['Password']}') returning IdUtilisateur"
        conn = connect_pg.connect()
        try:
            returnStatement = connect_pg.execute_commands(conn, query)
            idUser = returnStatement
        except Exception as e:
            if e.pgcode == errorcodes.UNIQUE_VIOLATION:
                # Erreur violation de contrainte unique
                return jsonify({'error': str(apiException.DonneeExistanteException(user['Username'], "Username", "utilisateur"))}), 400
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500

        try : 
            #switch case pour le role
            if json_data['role'] == "admin":
                query = f"Insert into edt.admin (IdUtilisateur) values ({idUser}) returning IdUtilisateur"
            elif json_data['role'] == "professeur":
                query = f"Insert into edt.professeur (initiale , idsalle , Idutilisateur) values ('{user['info']['initiale']}' , '{user['info']['idsalle']}' ,'{idUser}') returning idProf" 
                
            elif json_data['role'] == "eleve":
                query = f"Insert into edt.Eleve (idgroupe , Idutilisateur) values ('{user['info']['idgroupe']}' , '{idUser}') returning IdUtilisateur"
            returnStatement = connect_pg.execute_commands(conn, query)
            
            if json_data['role'] == "professeur":
                if(user['info']['isManager'] ):
                    query = f"Insert into edt.manager (IdProf, idGroupe) values ('{returnStatement}' , '{user['info']['idgroupe']}') returning IdUtilisateur"
                    returnStatement = connect_pg.execute_commands(conn, query)
        except Exception as e :
            connect_pg.disconnect(conn)
            conn = connect_pg.connect()
            query =f'delete from edt.utilisateur where idutilisateur = {idUser}'
            returnStatement = connect_pg.execute_commands(conn , query)
            return jsonify({"error" : "info part is wrong "}) , 400
        finally : 
            connect_pg.disconnect(conn)

    return jsonify({"success" : "user was added"}), 200

@user.route('/utilisateurs/auth', methods=['POST'])
def auth_utilisateur():
    """ Permet d'authentifier un utilisateur via la route /utilisateurs/auth
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    
    :param PassWord: mot de passe de l'utilisateur spécifié dans le body
    :type PassWord: String

    :raises DonneeIntrouvableException: Impossible de trouver l'Username spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’Username est invalide
    
    :return: jwt token
    :rtype: str
    """

    request.headers.get('Authorization')
    basic_auth = request.headers.get('Authorization')
    if basic_auth is None:
        return jsonify({'message': str(apiException.AuthentificationFailedException())}), 401
    basic_auth = basic_auth.split(' ')
    if len(basic_auth) != 2:
        return jsonify({'message': str(apiException.AuthentificationFailedException())}), 401
    basic_auth = base64.b64decode(basic_auth[1]).decode('utf-8')
    basic_auth = basic_auth.split(':')
    if len(basic_auth) != 2:
        return jsonify({'message': str(apiException.AuthentificationFailedException())}), 401
    username = basic_auth[0]
    password = basic_auth[1]
    password = util.password_encode(password)

    query = util.get("Utilisateur", {"Username": username}, ["Password", "FirstLogin" , "idutilisateur"])
    conn = connect_pg.connect()

    try:
        rows = connect_pg.get_query(conn, query[0], query[1])

    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur", "récuperer"))}), 500
    
    if (type(username) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("username", "string"))}), 400
    if (not rows):
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", username))}), 444
    
    
    if (rows[0][0] == password):
       accessToken =  create_access_token(identity=rows[0][2])
       return jsonify(accessToken=accessToken, firstLogin=rows[0][1])
   
    return jsonify({'error': str(apiException.LoginOuMotDePasseInvalideException())}), 400


#password update route wich update the password and the firstLogin column
@user.route('/utilisateurs/password/update', methods=['PUT'])
@jwt_required()
def update_utilisateur_password():
    """ Permet à un utilisateur de définir un mot de passe lors de la première connexion via la route /utilisateurs/password/update
    
    :param password: mot de passe définie par le nouvel utilisateur spécifié dans le body
    :type password: String

    :raises ParamètreTypeInvalideException: Le type de password doit être un string non vide
    :raises ActionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur

    :return: un message de succès
    :rtype: json
    
    """
    # username = get_jwt_identity()
    idUser = get_jwt_identity()
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    if(json_data['Password'] == ""):
        return jsonify({'error': str(apiException.ParamètreInvalideException("password", "string"))}), 400
    # Encode password
    json_data['Password'] = util.password_encode(json_data['Password'])

    json_data["FirstLogin"] = False
    table_name = "Utilisateur"
    keys = ["Password", "FirstLogin"]
        
    #using %S to avoid sql injection
    request1 = "update edt.utilisateur set password = %s , firstlogin = 'false' where idutilisateur = %s"
    values = (json_data['Password'], idUser)
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, request1, values)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500
    connect_pg.disconnect(conn)
    return jsonify({'success': 'mot de passe modifié'}), 200


@user.route('/utilisateurs/changerGroupeManager/<idManager>', methods=['PUT'])
@jwt_required()
def changer_groupe_manager(idManager):
    """ Permet à un utilisateur de définir un mot de passe lors de la première connexion via la route /utilisateurs/changerGroupeManager/<idManager>
    
    :param idManager: id du manager dont on doit changer le groupe
    :type idManager: int

    :param idGroupe: id du nouveau groupe à assigner au manager spécifié dans le body
    :type idGroupe: int

    :raises ParamètreTypeInvalideException: Les paramètres d'entrées doivent être de type numérique
    :raises ParamètreBodyManquantException: Un des paramètres spécifié dans le body est manquant
    :raises ActionImpossibleException: Impossible de mettre à jour le manager spécifié dans la table Manager

    :return: un message de succès
    :rtype: json
    
    """

    json_data = request.get_json()

    if 'idGroupe' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if (not idManager.isdigit() or type(json_data['idGroupe']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idManager ou idGroupe", "numérique"))}), 400
    
    query = f"update edt.manager set idGroupe='{json_data['idGroupe']}' where idManager='{idManager}'"
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, query)
    except (Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Manager", "mettre à jour"))}), 500
    connect_pg.disconnect(conn)
    return jsonify({'success': 'groupe modifié'}), 200
    
        
    
@user.route('/utilisateurs/update/<id>', methods=['PUT','GET'])
@jwt_required()
def update_utilisateur(id):
    """Permet de modifier un utilisateur via la route /utilisateurs/update/<id>
    
    :param id: id d'un utilisateurs
    :type id: int

    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String

    :raises ActionImpossibleException: Impossible de modifier l'utilisateur spécifié dans la table utilisateur
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour effectuer l'action

    :return: l'id de l'utilisateur modifié
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    if 'role' in json_data.keys():
        return jsonify({'error ': 'le role ne peut pas etre modifié pour l\'instant'}), 400
    # TODO: finish role vérification (use Enum)
    if (json_data['role'] != "admin" and json_data['role'] != "professeur" and json_data['role'] != "eleve" and json_data['role'] != "manager"):
        return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400

    if "info" not in json_data.keys():
        return jsonify({'error': 'missing "info" part of the body'}), 400
    
    req = "update edt.utilisateur set "
    if 'FirstName' in json_data.keys():
        req += f"firstname = '{json_data['FirstName']}' , "
    if 'LastName' in json_data.keys():
        req += f"lastname = '{json_data['LastName']}' , "
    if 'Username' in json_data.keys():
        req += f"username = '{json_data['Username']}' , "
    if 'Password' in json_data.keys():
        json_data['Password'] = util.password_encode(json_data['Password'])
        req += f"password = '{json_data['Password']}'"
    
    if req[-2:] == ", ":
        req = req[:-2]

    req += f" where idutilisateur={id}"
    
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, req)
    except Exception as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
           
            return jsonify({'error': str(apiException.DonneeExistanteException(json_data['Username'], "Username", "utilisateur"))}), 400
        else:
            
            return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500
    
    return jsonify({'success': 'utilisateur modifié'}), 200


@user.route('/utilisateurs/delete/<id>', methods=['DELETE'])
@jwt_required()
def delete_utilisateur(id):
    """Permet de supprimer un utilisateur via la route /utilisateurs/delete/<id>
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String

    :raises ActionImpossibleException: Impossible de supprimer l'utilisateur spécifié dans la table utilisateur
    :raises PermissionManquanteException: Si l'utilisateur n'a pas assez de droit pour effectuer l'action 

    :return: l'id de l'utilisateur supprimé
    :rtype: json
    """

    #check if the user is admin
    conn = connect_pg.connect()

    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    tabQuery = []
    query = f"delete from edt.utilisateur where idutilisateur={id}"
    tabQuery.append(query)
    conn = connect_pg.connect()

    permission = perm.getUserPermission(id, conn)
    
    if(permission[0] == 0):#En fonction du role de l'utilisateur, on supprime les dépendances(clée étrangère) de idUtlisateurs
        query2 = f"delete from edt.admin where idutilisateur={id}"
        tabQuery.append(query2)

    elif(permission[0] == 1):
        query2 = f"delete from edt.professeur where idutilisateur={id}"
        query3 = f"delete from edt.manager where idProf={permission[1][0][1]}"
        tabQuery.append(query2)
        tabQuery.append(query3)

    elif(permission[0] == 2):
        query2 = f"delete from edt.professeur where idutilisateur={id}" 
        query3 = f"delete from edt.enseigner where idProf={permission[1][0][0]}"
        query4 = f"delete from edt.responsable where idProf={permission[1][0][0]}"
        tabQuery.append(query2)
        tabQuery.append(query3)
        tabQuery.append(query4)
    
    elif(permission[0] == 3):
        query2 = f"delete from edt.eleve where idutilisateur={id}"
        tabQuery.append(query2)

    try:
        for k in range(len(tabQuery) - 1, -1 , -1): # fonctionnement en pile
            connect_pg.execute_commands(conn, tabQuery[k])

    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur","supprimer"))}), 500
    
    return jsonify({'success': 'utilisateur supprimé'}), 200


@user.route('/utilisateurs/getAllManager', methods=['GET','POST'])
@jwt_required()
def get_all_manager():
    """Renvoit tous les managers via la route /utilisateurs/getAllManager
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    
    :return: tous les managers
    :rtype: flask.wrappers.Response
    """
    returnStatement = []
    conn = connect_pg.connect()
    query = f"Select * from edt.manager order by idManager asc"
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Manager"))}), 400
        for row in rows:
            returnStatement.append(get_manager_statement(row)) #TODO : get_manager_statement n'existe pas
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Manager", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

        
@user.route('/utilisateurs/getManagerGroupe/<idGroupe>', methods=['GET','POST'])
@jwt_required()
def get_manager_groupe(idGroupe):
    """Renvoit le manager d'un groupe via la route /utilisateurs/getManagerGroupe/<idGroupe>

    :param idGroupe: id du groupe à rechercher
    :type idGroupe: int

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un get dans la table manager
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table manager
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: un manager
    :rtype: json
    """
    
    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    conn = connect_pg.connect()
    
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    query = f"select * from edt.manager where idGroupe = {idGroupe} order by idManager asc"
    
    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Manager"))}), 400
        for row in rows:
            returnStatement = get_manager_statement(rows[0])
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Manager", "récupérer"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@user.route('/utilisateurs/getManager/<idManager>', methods=['GET','POST'])
@jwt_required()
def get_one_manager(idManager):
    """Renvoit un manager de par son id via la route /utilisateurs/getManager/<idManager>

    :param idManager: id du groupe à rechercher
    :type idManager: int

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un get/id dans la table manager
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table manager
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: un manager
    :rtype: json
    """
    
    if (not idManager.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idManager", "numérique"))}), 400
    
    conn = connect_pg.connect()
    
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    query = f"select * from edt.manager where idManager = {idManager}"
    
    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Manager"))}), 400
        for row in rows:
            returnStatement = get_manager_statement(rows[0])
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Manager", "récupérer"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

    
#TODO : DEBUG ROUTE TO DELETE 
@user.route('/utilisateurs/getPermission', methods=['GET','POST'])
@jwt_required()
def getPermission():
    """Permet de récupérer la permission d'un utilisateur via la route /utilisateurs/getPermission
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises ActionImpossibleException: Impossible de récupérer la permission de l'utilisateur spécifié dans la table utilisateur
    
    :return: la permission de l'utilisateur
    :rtype: json
    """
    user_id = get_jwt_identity()
    conn = connect_pg.connect()
    return jsonify(perm.getUserPermission(user_id , conn)[0])