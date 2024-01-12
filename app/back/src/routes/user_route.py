from flask import Blueprint, request, jsonify
from flask_cors import CORS
import flask

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.user_service import get_utilisateur_statement, get_professeur_statement, get_professeur_statement_extended
import src.services.permision as perm
import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error
import src.services.verification as verif 

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import json
import datetime
user = Blueprint('user', __name__)

# TODO: refactor user

@user.route('/user/getProfDispo', methods=['GET', 'POST'])
@jwt_required()
def get_prof_dispo():
    """Renvoit tous les professeurs disponible sur une période via la route /user/getProfDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la période spécifié dans le body
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
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    
    if 'HeureDebut' not in json_datas or 'Jour' not in json_datas or 'NombreHeure' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if not verif.estDeTypeTime(json_datas['HeureDebut']) or not verif.estDeTypeTimeStamp(json_datas['Jour']) or not verif.estDeTypeTime(json_datas['NombreHeure']):
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

    query = f""" select distinct edt.professeur.* from edt.professeur full join edt.enseigner using(idProf) full join edt.cours
    using(idCours) where (idProf is not null) and ( '{json_datas['HeureDebut']}' <  HeureDebut 
    and  '{str(HeureFin)}' <= HeureDebut or '{json_datas['HeureDebut']}'::time >=  (HeureDebut + NombreHeure::interval)) 
    or ('{json_datas['Jour']}' != Jour and idProf is not null) or (HeureDebut is null) order by idProf asc
    """
    conn = connect_pg.connect()
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Aucun professeur disponible n'a été trouvé à la période spécifié"))}), 400
        
        for row in rows:
            returnStatement.append(get_professeur_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Enseigner", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)



@user.route('/utilisateurs/getAll', methods=['GET','POST'])
@jwt_required()
def get_utilisateur():
    """Renvoit tous les utilisateurs via la route /utilisateurs/get

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table utilisateur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table utilisateur
    
    :return:  tous les utilisateurs
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'erreur': str(apiException.PermissionManquanteException())}), 403
    
    query = "select * from edt.utilisateur order by IdUtilisateur asc"
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    try:
        for row in rows:
            returnStatement.append(get_utilisateur_statement(row))
    except(TypeError) as e:
        return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)



@user.route('/utilisateurs/getProfE', methods=['GET','POST'])
@jwt_required()
def get_prof_etendue():
    """Renvoit tous les professeurs avec des informations de la table utilisateur via la route /utilisateurs/get

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table prof/utilisateur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table utilisateur/prof
    
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
        return jsonify({'erreur': str(apiException.InsertionImpossibleException("professeur", "récupérer"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/getAllProf', methods=['GET','POST'])
@jwt_required()
def get_prof():
    """Renvoit tous les profs via la route /utilisateurs/getAllProf

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    
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

    :param idSae: id d'une ressource représentant une sae que l'on veut écarter du calcul des heures travaillés spécifié via le body
    :type idSae: int(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    
    :return:  tous les professeurs
    :rtype: json
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()
    querySae = ""
    try:
        json_datas = request.get_json()
        if 'idSae' in json_datas:
            if (type(json_datas['idSae']) != int):
                return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSae", "numérique"))}), 400
            querySae += f" and (idRessource != {json_datas['idSae']}) "

    except(Exception) as e: # Si aucune idSae n'es fournie
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

    :param idSae: id d'une ressource représentant une sae que l'on veut écarter du calcul des heures travaillés spécifié via le body
    :type idSae: int(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    
    :return:  tous les professeurs
    :rtype: json
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()
    querySae = ""
    try:
        json_datas = request.get_json()
        if 'idSae' in json_datas:
            if (type(json_datas['idSae']) != int):
                return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSae", "numérique"))}), 400
            querySae += f" and (idRessource != {json_datas['idSae']}) "

    except(Exception) as e: # Si aucune idSae n'es fournie
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


@user.route('/utilisateurs/getProfHeureTravaillerMois/<idProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_heure_travailler_mois(idProf):
    """Renvoit toutes les heures faites par un prof lors d'un mois via la route /utilisateurs/getProfHeureTravaillerMois/<idProf>

    :param idProf: id d'un professeur présent dans la base de donnée
    :type idProf: int

    :param mois: mois à calculer au format YYYY-MM (ex : 2023-12) à spécifié dans le body
    :type mois: str

    :param idSae: id d'une ressource représentant une sae que l'on veut écarter du calcul des heures travaillés spécifié via le body
    :type idSae: int(optionnel)

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un getAll dans la table professeur
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table professeur
    
    :return:  tous les professeurs
    :rtype: json
    """

    if (not idProf.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idProf", "numérique"))}), 400
    
    conn = connect_pg.connect()
    querySae = ""
    try:
        json_datas = request.get_json()
        if 'idSae' in json_datas:
            if (type(json_datas['idSae']) != int):
                return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSae", "numérique"))}), 400
            querySae += f" and (idRessource != {json_datas['idSae']}) "

    except(Exception) as e: # Si aucune idSae n'es fournie
        pass

    dateAujourdhui = str(datetime.date.today())
    heureActuelle = str(datetime.datetime.now())

    query = f"""select sum(nombreheure) as nombreheureTravailler from edt.cours inner join edt.enseigner 
    using(idCours)  where idProf = {idProf} and ((jour < '{dateAujourdhui}') or (jour = '{dateAujourdhui}' 
    and (HeureDebut + NombreHeure::interval) < '{heureActuelle}'::time)){querySae} 
    and TO_CHAR(jour, 'YYYY-MM') = '{json_datas['mois']}';
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


@user.route('/utilisateurs/getProfParInitiale/<initialeProf>', methods=['GET','POST'])
@jwt_required()
def get_prof_par_initiale(initialeProf):
    """Renvoit un prof via ses initiales via la route /utilisateurs/getProfParInitiale/<idProf>

    :param initialeProf: initiale d'un professeur présent dans la base de donnée
    :type initialeProf: str

    :raises PermissionManquanteException: Si pas assez de droit pour effectuer un get dans la table professeur
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
    
    :return:  tous les enseignants
    :rtype: json
    """
    
    #check if the user is admin
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
    
    :return: un professeur
    :rtype: json
    """
    
    #check if the user is admin
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
    
    :return:  l'utilisateur connecté
    :rtype: json
    """
    user_id = get_jwt_identity()
    conn = connect_pg.connect()
    
    
    query = f"select idUtilisateur,FirstName,LastName,Username from edt.utilisateur where idutilisateur = {user_id}"
    user_rows = connect_pg.get_query(conn, query)
    

    if not user_rows:
        connect_pg.disconnect(conn)
        return jsonify({'erreur': str(apiException.AucuneDonneeTrouverException("utilisateur"))}), 404
    
    user = {
        "idUtilisateur": user_rows[0][0],
        "FirstName": user_rows[0][1],
        "LastName": user_rows[0][2],
        "Username": user_rows[0][3]
    }
    
    
    role_query = f"select IDAdmin from edt.admin where idUtilisateur = {user_id}"
    role_rows = connect_pg.get_query(conn, role_query)
    
    if role_rows:
        role = {
        "type": "Administrateur",
        "id": role_rows[0][0]
        }
        user["role"] = role
        connect_pg.disconnect(conn)
        return jsonify(user)
    
    role_query = f"SELECT p.idProf, p.Initiale, s.Numero FROM edt.professeur as p JOIN edt.salle as s ON p.idSalle = s.idSalle WHERE p.idUtilisateur = {user_id}"
    role_rows = connect_pg.get_query(conn, role_query)

    if role_rows:
        role = {
        "type": "Enseignant",
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
        "type": "Élève",
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
    
    :raises DonneeIntrouvableException: Impossible de trouver l'userName spécifié dans la table utilisateur
    :raises ParamètreTypeInvalideException: Le type de l’userName est invalide, un string est attendue
    
    :return:  l'utilisateur a qui appartient cette userName
    :rtype: json
    """
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 3 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    query = f"select * from edt.utilisateur where Username='{userName}'"

    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if (userName.isdigit() or type(userName) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("userName", "string"))}), 400
    try:
        if len(rows) > 0:
            returnStatement = get_utilisateur_statement(rows[0])
    except(TypeError) as e:
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", userName))}), 404
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@user.route('/utilisateurs/add', methods=['POST'])
@jwt_required()
def add_utilisateur():
    """Permet d'ajouter un utilisateur via la route /utilisateurs/add
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    
    :raises ActionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur crée
    :rtype: json

    """
    #{ "role": "eleve", "users": [ { "firstName": "Elève1", "lastName": "lastName", "info": { "idGroupe": "1", "idSalle": "", "isManager": "" } }, { "firstName": "Elève2", "lastName": "lastName", "info": { "idGroupe": "2", "idSalle": "", "isManager": "" } } ] } 
    
    #check if the user is admin
    conn = connect_pg.connect()
    json_datas = request.get_json()
    # if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
    #     return jsonify({'error': 'not enough permission'}), 403

    # TODO: use nom salle in create user instead of id salle

    if not json_datas:
            return jsonify({'error ': 'missing json body'}), 400
    
    if (json_datas['role'] != "admin" and json_datas['role'] != "professeur" and json_datas['role'] != "eleve" and json_datas['role'] != "manager"):
        return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    for user in json_datas['users']:
        conn = connect_pg.connect()

        if "info" not in user.keys():
            return jsonify({'error': 'missing "info" part of the body'}), 400
        
        key = ["FirstName", "LastName", "Username", "Password"]
        for k in user.keys():
            if k in key:
                key.remove(k) 
        if len(key) != 0:
            return jsonify({'error ': 'missing ' + str(key)}), 400 
        
        query = f"Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{user['FirstName']}', '{user['LastName']}', '{user['Username']}', '{user['Password']}') returning IdUtilisateur"
        conn = connect_pg.connect()
        try:
            returnStatement = connect_pg.execute_commands(conn, query)
            idUser = returnStatement
        except psycopg2.IntegrityError as e:
            if e.pgcode == errorcodes.UNIQUE_VIOLATION:
                # Erreur violation de contrainte unique
                return jsonify({'error': str(apiException.DonneeExistanteException(user['Username'], "Username", "utilisateur"))}), 400
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500

        
        try : 
            
            #switch case pour le role
            if json_datas['role'] == "admin":
                query = f"Insert into edt.admin (IdUtilisateur) values ({idUser}) returning IdUtilisateur"
            elif json_datas['role'] == "professeur":
                query = f"Insert into edt.professeur (initiale , idsalle , Idutilisateur) values ('{user['info']['initiale']}' , '{user['info']['idsalle']}' ,'{idUser}') returning idProf" 
                
            elif json_datas['role'] == "eleve":
                query = f"Insert into edt.Eleve (idgroupe , Idutilisateur) values ('{user['info']['idgroupe']}' , '{idUser}') returning IdUtilisateur"
            returnStatement = connect_pg.execute_commands(conn, query)
            
            if json_datas['role'] == "professeur":
                if(user['info']['isManager'] ):
                    query = f"Insert into edt.manager (IdProf) values ({returnStatement}) returning IdUtilisateur"
                    returnStatement = connect_pg.execute_commands(conn, query)
                
                

            
            
        except Exception as e :
            print(e)
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
    try:
        json_datas = request.get_json()
    except (Exception) as error:
        print(error)
    json_datas = request.get_json()
    username = json_datas['Username']
    password = json_datas['Password']
    query = f"select Password, FirstLogin , idutilisateur from edt.utilisateur where Username='{username}'"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    if (type(username) != str):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("username", "string"))}), 400
    if (not rows):
        
        return jsonify({'error': str(apiException.DonneeIntrouvableException("utilisateur", username))}), 404
    
    
    if (rows[0][0] == password):
       accessToken =  create_access_token(identity=rows[0][2])
       return jsonify(accessToken=accessToken, firstLogin=rows[0][1])
   
    return jsonify({'error': str(apiException.LoginOuMotDePasseInvalideException())}), 400


#password update route wich update the password and the firstLogin column
@user.route('/utilisateurs/password/update', methods=['PUT'])
@jwt_required()
def update_utilisateur_password():
    """ Permet à un utilisateur de définir un mot de passe lors de la première connexion via la route /utilisateurs/firstLogin
    
    :param password: mot de passe définie par le nouvel utilisateur spécifié dans le body
    :type password: String

    :raises ParamètreTypeInvalideException: Le type de password doit être un string non vide
    :raises ActionImpossibleException: Impossible d'ajouter l'utilisateur spécifié dans la table utilisateur
    

    """
    username = get_jwt_identity()
    json_datas = request.get_json()
    password = json_datas['Password']
    if(password == ""):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("password", "string"))}), 400    
    query = f"update edt.utilisateur set Password='{password}', FirstLogin=false where Username='{username}'"
    conn = connect_pg.connect()
    try:
        
        connect_pg.execute_commands(conn, query)
    except:
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500
    connect_pg.disconnect(conn)
    
    
        
    
@user.route('/utilisateurs/update/<id>', methods=['PUT','GET'])
@jwt_required()
def update_utilisateur(id):
    """Permet de modifier un utilisateur via la route /utilisateurs/update
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises ActionImpossibleException: Impossible de modifier l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur modifié
    :rtype: json
    """
    
    #check if the user is admin
    conn = connect_pg.connect()
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    
    json_datas = request.get_json()
    if not json_datas:
        return jsonify({'error ': 'missing json body'}), 400
    if 'role' in json_datas.keys():
        return jsonify({'error ': 'le role ne peut pas etre modifié pour l\'instant'}), 400
    # TODO: finish role vérification (use Enum)
        if (json_datas['role'] != "admin" and json_datas['role'] != "professeur" and json_datas['role'] != "eleve" and json_datas['role'] != "manager"):
            return jsonify({'error ': 'le role doit etre admin ,professeur, eleve ou manager'}), 400
    
        if "info" not in json_datas.keys():
            return jsonify({'error': 'missing "info" part of the body'}), 400
    
    #req = "Insert into edt.utilisateur (FirstName, LastName, Username, PassWord) values ('{json_datas['FirstName']}', '{json_datas['LastName']}', '{json_datas['Username']}', '{json_datas['Password']}') returning IdUtilisateur" 

    req = "update edt.utilisateur set "
    if 'FirstName' in json_datas.keys():
        req += f"firstname = '{json_datas['FirstName']}' , "
    if 'LastName' in json_datas.keys():
        req += f"lastname = '{json_datas['LastName']}' , "
    if 'Username' in json_datas.keys():
        req += f"username = '{json_datas['Username']}' , "
    if 'Password' in json_datas.keys():
        req += f"password = '{json_datas['Password']}'"
    
    #remove "and" if there is no update
    if req[-2:] == ", ":
        req = req[:-2]

    req += f" where idutilisateur={id}"
    #update edt.utilisateur set firstname = 'bastien2' where idutilisateur = 8
    
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, req)
    except psycopg2.IntegrityError as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
           
            return jsonify({'error': str(apiException.DonneeExistanteException(json_datas['Username'], "Username", "utilisateur"))}), 400
        else:
            
            return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur"))}), 500
    
    return jsonify({'success': 'utilisateur modifié'}), 200


@user.route('/utilisateurs/delete/<id>', methods=['DELETE'])
@jwt_required()
def delete_utilisateur(id):
    """Permet de supprimer un utilisateur via la route /utilisateurs/delete
    
    :param Username: login de l'utilisateur spécifié dans le body
    :type Username: String
    :raises ActionImpossibleException: Impossible de supprimer l'utilisateur spécifié dans la table utilisateur
    
    :return: l'id de l'utilisateur supprimé
    :rtype: json
    """

    #check if the user is admin
    conn = connect_pg.connect()
    """
    if not perm.permissionCheck(get_jwt_identity() , 0 , conn):
        return jsonify({'error': 'not enough permission'}), 403
    """
    
    json_datas = request.get_json()
    tabQuery = []
    query = f"delete from edt.utilisateur where idutilisateur={id}"
    tabQuery.append(query)
    conn = connect_pg.connect()

    permission = perm.getUserPermission(id, conn)
    
    if(permission[0] == 0):
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

    except psycopg2.IntegrityError as e:
        
       
        return jsonify({'error': str(apiException.ActionImpossibleException("utilisateur","supprimer"))}), 500
    
    return jsonify({'success': 'utilisateur supprimé'}), 200

        
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
    return jsonify(perm.getUserPermission(user_id , conn))






    


