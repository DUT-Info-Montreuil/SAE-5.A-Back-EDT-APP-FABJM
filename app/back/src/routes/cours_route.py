from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.cours_service import *
from src.services.user_service import get_professeur_statement

from src.routes.groupe_route import get_groupe_cours 

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error
import src.services.permision as perm
import json
import src.services.verification as verif 
from datetime import date

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import datetime

cours = Blueprint('cours', __name__)


@cours.route('/cours/getAll', methods=['GET'])
@jwt_required()
def getAll_cours():
    """Renvoit toutes les cours via la route /cours/getAll

    
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table cours
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table cours
    
    
    :return: toutes les cours
    :rtype: json
    """
    conn = connect_pg.connect()
    
    query = "select * from edt.cours order by idCours asc"
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

@cours.route('/cours/getAllCourProf', methods=['GET'])
@jwt_required()
def getAll_cours_prof():
    """Renvoit toutes les cours auquel ont été assigné des professeurs via la route /cours/getAll

    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table cours
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table cours
    
    :return: toutes les cours ayant au moin un enseignant
    :rtype: json
    """
    conn = connect_pg.connect()
    
    query = "select distinct edt.cours.* from edt.cours inner join edt.enseigner using(idCours) order by idCours asc"
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("enseigner"))}), 404
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/get/<idCours>', methods=['GET'])
@jwt_required()
def get_cours(idCours):
    """
    Renvoit un cours spécifié par son idGroupe via la route /cours/get/<idCours>

    :param idCours: l'id d'un cours présent dans la base de donnée
    :type idCours: str

    :raises DonneeIntrouvableException: Impossible de trouver l'idCours spécifié dans la table cours
    :raises ParamètreTypeInvalideException: Si le paramètre idCours n'est pas une valeur numérique
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données dans la table cours 

    :return:  le cours a qui appartient cet id
    :rtype: json
    """

    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400

    query = f"select * from edt.cours where idCours='{idCours}'"
    conn = connect_pg.connect()

    returnStatement = {}
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("cours", idCours))}), 404
        returnStatement = get_cours_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/getSpe', methods=['GET','POST'])
@jwt_required()
def get_cours_spe():
    """Renvoit les cours spécifique à un utilisateur si possible sinon renvoit les cours générale via la route /cours/get
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critère dans la table cours
    :raises ActionImpossibleException: Si une erreur est survenue de la récupération des données
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé dans la table cours
    
    :return: Les cours 
    :rtype: json
    """

    conn = connect_pg.connect()
    if(perm.getUserPermission(get_jwt_identity() , conn)[0] == 2):
        returnStatement = []
        try:
            rows = getCoursProf(get_jwt_identity() , conn)
            if rows == []:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
            for row in rows:
                returnStatement.append(get_cours_statement(row))
        except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("cours","récupérer"))}), 500
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    
    elif(perm.getUserPermission(get_jwt_identity() , conn)[0] == 3):
        returnStatement = []
        try:
            idGroupe = connect_pg.get_query(conn , f"select idGroupe from edt.eleve where idUtilisateur ={get_jwt_identity()}")[0][0]
            rows = getCoursGroupeService(idGroupe , conn)
            if rows == []:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("enseigner"))}), 404
            for row in rows:
                returnStatement.append(get_cours_statement(row))
        except(Exception) as e:
            return jsonify({'error': str(apiException.ActionImpossibleException("cours","récupérer"))}), 500
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
            return jsonify({'error': str(apiException.ActionImpossibleException("cours", "récuperer"))}), 500
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)




@cours.route('/cours/getCoursSemestre/<idSemestre>', methods=['GET','POST'])
@jwt_required()
def get_cours_semestre(idSemestre):
    """Renvoit toutes les cours d'un semestre via la route /cours/getCoursSemestre/<idSemestre>

    :raises PermissionManquanteException: Si pas assez de droit pour récupérer toutes les données présentes dans la table cours
    :raises AucuneDonneeTrouverException: Une aucune donnée n'a été trouvé dans la table cours
    :raises ParamètreTypeInvalideException: Si le paramètre idSemestre n'est pas une valeur numérique
    
    :return: toutes les cours d'un semestre
    :rtype: json
    """

    if (not idSemestre.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSemestre", "numérique"))}), 400
    
    query = f"select edt.cours.* from edt.cours inner join edt.ressource using(idRessource) inner join edt.semestre using(idSemestre) where idSemestre = {idSemestre} order by idCours"
    conn = connect_pg.connect()
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("Cours"))}), 404
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Cours", "récupérer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/getCoursGroupe/<idGroupe>', methods=['GET','POST'])
@jwt_required()
def get_cours_groupe(idGroupe):
    """Renvoit les cours d'un groupe via la route /cours/getSalle/<idCours>
    
    :param idGroupe: id du groupe à rechercher
    :type idGroupe: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    :raises ParamètreTypeInvalideException: Si le paramètre idGroupe n'est pas une valeur numérique
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """

    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idGroupe", "numérique"))}), 400
    
    returnStatement = []
    conn = connect_pg.connect()
    try:
        rows = getCoursGroupeService(idGroupe , conn)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Etudier",idGroupe))}), 400
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Cours, Etudier et Groupe", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/getCoursGroupeExtended/<idGroupe>', methods=['GET','POST'])
@jwt_required()
def get_cours_groupe_extended(idGroupe):
    """Renvoit les cours d'un groupe via la route /cours/getSalle/<idCours>
    
    :param idGroupe: id du groupe à rechercher
    :type idGroupe: int

    :param intervalleDebut: date de debut de l'intervalle au format DATE(yyyy-mm-dd)
    :type intervalleDebut: str

    :param intervalleFin: date de fin de l'intervalle au format DATE(yyyy-mm-dd)
    :type intervalleFin: str

    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreTypeInvalideException: Si un paramètre n'est pas au format DATE(yyyy-mm-dd)
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """
    json_data = request.get_json()
    returnStatement = []
    conn = connect_pg.connect()
    
    if (not idGroupe.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    if 'intervalleDebut' not in json_data  or 'intervalleFin' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    if not verif.estDeTypeDate(json_data['intervalleDebut']) or not verif.estDeTypeDate(json_data['intervalleFin']):
        return jsonify({'error': str(apiException.ParamètreInvalideException("intervalleDebut, intervalleFin"))}), 404
    
    intervalleDebut = json_data['intervalleDebut']
    intervalleFin = json_data['intervalleFin']
    intervalleDebut = date(int(intervalleDebut[:4]), int(intervalleDebut[5:7]), int(intervalleDebut[8:10]))
    intervalleFin = date(int(intervalleFin[:4]), int(intervalleFin[5:7]), int(intervalleFin[8:10]))

    
    if intervalleDebut > intervalleFin:
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure"))}), 404

    query = f"""Select s1.idSalle, s1.nom as nomSalle, s1.capacite, edt.cours.*,edt.ressource.*, g1.idGroupe, g1.nom as nomGroupe, g1.idGroupeParent ,
    e1.idProf, e1.initiale, e1.idSalle, e1.idUtilisateur from edt.cours full join edt.accuellir using (idCours) full join edt.salle as s1 using(idSalle) 
    full join edt.ressource using(idRessource) full join edt.enseigner using(idCours) full join edt.etudier as e2 using(idCours) 
    full join edt.groupe as g1 using(idGroupe) full join edt.professeur as e1 using(idProf) where e2.idGroupe = {idGroupe} 
    and ( jour >= '{json_data["intervalleDebut"]}' and  jour <= '{json_data["intervalleFin"]}')
    """

    try:
        rows = connect_pg.get_query(conn , query)
        for row in rows:
            returnStatement.append(get_cours_groupe_extended_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Cours", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)




@cours.route('/cours/deplacer/<idCours>', methods=['PUT'])
@jwt_required()
def deplacer_cours(idCours):
    """Permet de déplacer un cours via la route /cours/deplacer/<idCours>
    
    :param idCours: id du cours à déplacer
    :type idCours: int

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) à spécifié dans le body
    :type HeureDebut: str 

    :param Jour: date de la journée où la disponibilité des groupes doit être vérifer au format DATE(yyyy-mm-dd) à spécifié dans le body
    :type Jour: str

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises ParamètreInvalideException: Si l'iut est fermé  ou que le groupe, le professeur ou la salle ne sont plus disponible durant la nouvelle période spécifié
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la mise à jour de la table cours
    
    :return: id du cours déplacer si présent
    :rtype: json
    """

    conn = connect_pg.connect()
    json_data = request.get_json()

    if 'HeureDebut' not in json_data and 'Jour' not in json_data:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    if 'HeureDebut' in json_data and not verif.estDeTypeTime(json_data['HeureDebut']):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("HeureDebut", "hh:mm:ss"))}), 400
    

    if 'Jour' in json_data and not verif.estDeTypeDate(json_data['Jour']):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("Jour", "yyyy-mm-dd"))}), 400
    
    
    # TODO: refactor
    
    
    cour = get_cours(idCours)
    if type(cour) != tuple :
        cour = json.loads(cour.data) 

        if 'HeureDebut' in json_data :
            HeureDebut = json_data['HeureDebut']
        else:
            HeureDebut = cour['HeureDebut']
        
        if 'Jour' in json_data :
            Jour = json_data['Jour']
        else:
            Jour = cour['Jour']

        NombreHeure = cour['NombreHeure']
        
        HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
        NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
        HeureFin = HeureDebut + NombreHeure

        heure_ouverture_iut = datetime.timedelta(hours = 8)
        heure_fermeture_iut = datetime.timedelta(hours = 19)

        if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé durant la période spécifié"))}), 404

        idGroupe = json.loads(get_groupe_cours(idCours).data)[0]['IdGroupe']

        HeureFin = str(HeureFin)
        
        if not verif.groupeEstDispo(idGroupe, HeureDebut, HeureFin, Jour, conn, idCours):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce groupe n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400
        
        idProf = json.loads(get_prof_cours(idCours).data)[0]['idProf']
        if not verif.groupeEstDispo(idProf, HeureDebut, HeureFin, Jour, conn, idCours):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce professeur n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400

        idSalle = json.loads(get_prof_cours(idCours).data)[0]['idSalle']
        if not verif.salleEstDispo(idSalle, HeureDebut, HeureFin, Jour, conn, idCours):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Cette salle n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400
    
    query = "UPDATE edt.cours "
    if 'HeureDebut' in json_data:
        query += f"SET HeureDebut = '{json_data['HeureDebut']}'"
    if 'Jour' in json_data:
        if 'HeureDebut' in json_data:
            query += f" , Jour = '{json_data['Jour']}'"
        else:
            query += f"SET Jour = '{json_data['Jour']}'"
    query += f" where idCours={idCours}"
    
    try:
        connect_pg.get_query(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Cours", "mettre à jour"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(idCours)
    
@cours.route('/cours/modifierCours/<idCours>', methods=['PUT'])
@jwt_required()
def modifier_cours(idCours):
    """Permet de modifier un cours via la route /cours/modifierCours/<idCours>
    
    :param idCours: id du cours à modifier
    :type idCours: int

    :param NombreHeure: NombreHeure à modifier spécifié dans le body si le cas
    :type NombreHeure: int(optionnel)

    :param idRessource: idRessource à modifier spécifié dans le body si le cas
    :type idRessource: int(optionnel)

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises DonneeIntrouvableException: Si aucune données remplisssant les critères n'a été trouvé 
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours modifier si présent
    :rtype: json
    """
    json_data = request.get_json()


    if 'NombreHeure' not in json_data and 'idRessource' not in json_data:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    
    if 'NombreHeure' in json_data and not verif.estDeTypeTime(json_data['NombreHeure']):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("NombreHeure", "hh:mm:ss"))}), 400
    
    cour = get_cours(idCours)
    
    query = "UPDATE edt.cours "
    if 'NombreHeure' in json_data:
        query += f"SET NombreHeure = '{json_data['NombreHeure']}'"
    if 'idRessource' in json_data:
        if 'NombreHeure' in json_data:
            query += f" , idRessource = '{json_data['idRessource']}'"
        else:
            query += f"SET idRessource = '{json_data['idRessource']}'"
    query += f" where idCours={idCours}"

    conn = connect_pg.connect()
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("enseigner"))}), 500
        
    if type(cour) == tuple : 
        return jsonify({'error': str(apiException.ActionImpossibleException("cours"))}), 500
    
    cour = json.loads(cour.data)
    aujourdhui = date.today()
    jourCours = date(int(cour['Jour'][:4]), int(cour['Jour'][5:7]), int(cour['Jour'][8:10]))
    HeureDebut = datetime.timedelta(hours = int(cour['HeureDebut'][:2]),minutes = int(cour['HeureDebut'][3:5]), seconds = 00)
    HeureActuelle = str(datetime.datetime.now())
    HeureActuelle = datetime.timedelta(hours = int(HeureActuelle[11:13]),minutes = int(HeureActuelle[14:16]), seconds = 00)
    newNombreHeure = (datetime.timedelta(hours = int(json_data['NombreHeure'][:2]),minutes = int(json_data['NombreHeure'][3:5]), seconds = 00)).total_seconds()
    oldNombreHeure = (datetime.timedelta(hours = int(cour['NombreHeure'][:2]),minutes = int(cour['NombreHeure'][3:5]), seconds = 00)).total_seconds()

    if( jourCours > aujourdhui  or (jourCours == aujourdhui and HeureDebut > HeureActuelle)):
        if ('NombreHeure' in json_data and json_data['NombreHeure'] != cour['NombreHeure']) and ('idRessource' not in json_data or json_data['idRessource'] == cour['idRessource']): # Si le nombreHeure a changé mais toujours dans la même ressource
            query = f"update edt.ressource set nbrheuresemestre =  ((nbrheuresemestre + {oldNombreHeure}) - {newNombreHeure} )  where idRessource = {cour['idRessource']}" # pour mettre à jour le nombre d'heures
            

        elif ('NombreHeure' not in json_data or json_data['NombreHeure'] == cour['NombreHeure']) and ('idRessource' in json_data and json_data['idRessource'] != cour['idRessource']): # Si le nombreHeure est inchangé mais que ce n'est plus la même ressource
            query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + {oldNombreHeure})  where idRessource = {cour['idRessource']}" 
            query2 = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre - {oldNombreHeure})  where idRessource = {json_data['idRessource']}" 
            connect_pg.execute_commands(conn, query2)
            
        
        elif ('NombreHeure' in json_data and json_data['NombreHeure'] != cour['NombreHeure']) and  ('idRessource' in json_data and json_data['idRessource'] != cour['idRessource']): # Si le nombreHeure a changé et que ce n'est plus la même ressource
            query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + {oldNombreHeure})  where idRessource = {cour['idRessource']}" 
            query2 = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre - {newNombreHeure})  where idRessource = {json_data['idRessource']}" 
            connect_pg.execute_commands(conn, query2)
            
        try:
            connect_pg.execute_commands(conn, query)
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23503':
                # Erreur violation de contrainte clée étrangère de la table Ressources
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", cour['idRessource']))}), 400
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "mettre à jour"))}), 500
                        
        
    connect_pg.disconnect(conn)
    return jsonify(idCours)
    




@cours.route('/cours/assignerProf/<idCours>', methods=['POST', 'PUT'])
@jwt_required()
def assignerProf(idCours):
    """Permet d'assigner un profeseur à un cours via la route /cours/assignerProf/<idCours>
    
    :param idCours: id du cours qui doit être superviser par un professeur
    :type idCours: int

    :param idProf: id du professeur à assigner à la ressource spécifié dans le body
    :type idProf: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser l'insertion

    :return: id du cours
    :rtype: int
    """
    json_data = request.get_json()
    
    if 'idProf' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    
    if (not idCours.isdigit() or type(json_data['idProf']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idProf", "numérique"))}), 400
    
    returnStatement = {}
    conn = connect_pg.connect()

    cour = get_cours(idCours)
    if type(cour) != tuple :
        cour = json.loads(get_cours(idCours).data) 

        HeureDebut = cour['HeureDebut']
        NombreHeure = cour['NombreHeure']
        HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00 )
        NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00 )
        HeureFin = str(HeureDebut + NombreHeure)

        if not verif.profEstDispo(json_data['idProf'], HeureDebut, HeureFin, cour['Jour'], conn, idCours):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce professeur n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400


    query = f"Insert into edt.enseigner (idProf, idCours) values ('{json_data['idProf']}', '{idCours}') returning idCours"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "prof" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Professeur ", json_data['idProf']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idCours = {idCours} et idProf = {json_data['idProf']}"
            messageColonne = f"idCours et idProf"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "enseigner"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("enseigner"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/getCoursSalle/<idSalle>', methods=['GET','POST'])
@jwt_required()
def get_cours_salle(idSalle):
    """Renvoit les cours se déroulant dans une salle via la route /cours/getCoursSalle/<idSalle>
    
    :param idSalle: id du cours à rechercher
    :type idSalle: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur survient durant la récupération des données
    :raises ParamètreTypeInvalideException: Si idSalle n'est pas une valeur numerique
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """

    if (not idSalle.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    
    query = f"Select edt.cours.* from edt.cours inner join edt.accuellir  using(idCours)  inner join edt.salle as e1 using (idSalle) where e1.idSalle = {idSalle} order by idCours asc"
    returnStatement = []
    conn = connect_pg.connect()
    
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Accuellir"))}), 400
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Accuellir", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


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
    json_data = request.get_json()
    if (not idCours.isdigit() or type(json_data['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idSalle", "numérique"))}), 400
    
    
    if 'idSalle' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if (not idCours.isdigit() or type(json_data['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idSalle", "numérique"))}), 400
    
    conn = connect_pg.connect()
    coursSalle = get_cours(idCours)
    
    if type(coursSalle) != tuple:
        coursSalle = json.loads(get_cours(idCours).data) 

        HeureDebut = coursSalle['HeureDebut']
        NombreHeure = coursSalle['NombreHeure']
        HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
        NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
        HeureFin = str(HeureDebut + NombreHeure)

        if not verif.salleEstDispo(json_data['idSalle'], HeureDebut, HeureFin, coursSalle['Jour'], conn,idCours):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Cette salle n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400
    
        
    
    returnStatement = {}
    query = f"Insert into edt.accuellir (idSalle, idCours) values ('{json_data['idSalle']}', '{idCours}') returning idCours"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "salle" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Salle ", json_data['idSalle']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idCours = {idCours} et idSalle = {json_data['idSalle']}"
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
    :raises ParamètreBodyManquantException: Si au moins un paramètre d'entrée attendu n'est spécifié dans le body
    :raises DonneeIntrouvableException: Une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser la mise à jour

    :return: id du cours dont la salle à changer
    :rtype: json
    """

    conn = connect_pg.connect()
    json_data = request.get_json()

    if 'idSalle' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    if (not idCours.isdigit() or type(json_data['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idSalle", "numérique"))}), 400
    
    cour = get_cours(idCours)
    if type(cour) != tuple:
        cour = json.loads(cour.data)
        if not verif.salleEstDispo(json_data['idSalle'], cour['HeureDebut'] ,cour['HeureFin'] , cour['Jour'], conn):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Cette salle n'est pas disponible durant la nouvelle période de cours spécifié"))}), 400
        
    query = f"update edt.accuellir set idSalle = {json_data['idSalle']}  where idCours={idCours}"
    
    
    try:
        connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "salle" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Salle ", json_data['idSalle']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idCours = {idCours} et idSalle = {json_data['idSalle']}"
            messageColonne = f"idCours et idSalle"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "accuellir"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("accuellir"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(idCours)

@cours.route('/cours/supprimerSalle/<idCours>', methods=['DELETE'])
@jwt_required()
def supprimer_salle(idCours):
    """Permet de supprimer une salle attribuer à un cours via la route /cours/supprimerSalle/<idCours>
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises ActionImpossibleException: Si une erreur survient lors de la suprression dans la table accuellir

    :return: id du cours supprimer si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    query = "delete from edt.accuellir where idCours=%(idCours)s" % {'idCours':idCours}
    conn = connect_pg.connect()
    try:
        rows = connect_pg.execute_commands(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("Accuellir", "supprimer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(idCours)


@cours.route('/cours/supprimer/<idCours>', methods=['DELETE'])
@jwt_required()
def supprimer_cours(idCours):
    """Permet de supprimer un cours via la route /cours/supprimer/<idCours>
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si aucune donnée répondant aux critères n'a été trouvés
    :raises ActionImpossibleException: Si une erreur lors de l'appel à la base de donnée 

    :return: id du cours supprimer si présent
    :rtype: json
    """

    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400

    conn = connect_pg.connect() 
    cour = get_cours(idCours)

    if type(cour) == tuple : 
        return jsonify({'error': str(apiException.ActionImpossibleException("cours","supprimé"))}), 500
    
    cour = json.loads(get_cours(idCours).data)
    aujourdhui = date.today()
    jourCours = date(int(cour['Jour'][:4]), int(cour['Jour'][5:7]), int(cour['Jour'][8:10]))
    HeureDebut = datetime.timedelta(hours = int(cour['HeureDebut'][:2]),minutes = int(cour['HeureDebut'][3:5]), seconds = 00)
    HeureActuelle = str(datetime.datetime.now())
    HeureActuelle = datetime.timedelta(hours = int(HeureActuelle[11:13]),minutes = int(HeureActuelle[14:16]), seconds = 00)
    NombreHeure = (datetime.timedelta(hours = int(cour['NombreHeure'][:2]),minutes = int(cour['NombreHeure'][3:5]), seconds = 00)).total_seconds()

    if( jourCours > aujourdhui  or (jourCours == aujourdhui and HeureDebut > HeureActuelle)):
        query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + {NombreHeure})  where idRessource = {cour['idRessource']}" # pour mettre à jour le nombre d'heures
        try:
            connect_pg.execute_commands(conn, query)
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23503':
                # Erreur violation de contrainte clée étrangère de la table Ressources
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", cour['idRessource']))}), 400
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "mettre à jour"))}), 500
    
    
    query = f"delete  from edt.cours where idCours={idCours}"
    query2 = f"delete  from edt.enseigner where idCours={idCours}"
    query3 = f"delete  from edt.etudier where idCours={idCours}"
    query3 = f"delete  from edt.accuellir where idCours={idCours}"
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, query3)
        connect_pg.execute_commands(conn, query2)
        connect_pg.execute_commands(conn, query)
    except Exception as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("cours","supprimé"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(idCours)
    

@cours.route('/cours/add', methods=['POST'])
@jwt_required()
def add_cours():
    """Permet d'ajouter un cours via la route /cours/add
    
    :param HeureDebut: date du début du cours spécifié au format TIME(hh:mm:ss) dans le body
    :type HeureDebut: str

    :param NombreHeure: durée du cours spécifié au format TIME(hh:mm:ss) dans le body
    :type NombreHeure: str

    :param Jour: date du cours au format DATE(yyyy-mm-dd) spécifié dans le body
    :type Jour: str

    :param idRessource: l'id d'une ressource présente dans la base de donnée spécifié dans le body
    :type idRessource: int

    :param typeCours: type du cours prenant une des  valeurs suivantes ['Amphi', 'Td', 'Tp', 'Sae'] spécifié dans le body
    :type typeCours: str
    
    :raises ActionImpossibleException: Impossible d'ajouter le cours spécifié dans la table cours
    :raises DonneeIntrouvableException: La valeur de la clée étrangère idRessource n'a pas pu être trouvé
    :raises ParamètreBodyManquantException: Si ou plusieurs paramètres sont manquant dans le body
    :raises ParamètreInvalideException: Si ou plusieurs paramètres sont incohérent ou invalide
    
    
    :return: l'id du cours qui vient d'être créé
    :rtype: int
    """
    json_data = request.get_json()
    if 'HeureDebut' not in json_data or 'NombreHeure' not in json_data or 'Jour' not in json_data or 'idRessource' not in json_data or 'typeCours' not in json_data:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    if not verif.estDeTypeTime(json_data['HeureDebut']) or not verif.estDeTypeDate(json_data['Jour']) or not verif.estDeTypeTime(json_data['NombreHeure']) or type(json_data['idRessource']) != int:
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure, idRessource ou Jour"))}), 404

    if type(json_data['typeCours']) != str or json_data['typeCours'] not in ['Amphi', 'Td', 'Tp', 'Sae']:
        return jsonify({'error': str(apiException.ParamètreInvalideException("typeCours"))}), 404

    HeureDebut = json_data['HeureDebut']
    NombreHeure = json_data['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = int(HeureDebut[6:8]))
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
    HeureFin = HeureDebut + NombreHeure

    heure_ouverture_iut = datetime.timedelta(hours = 8)
    heure_fermeture_iut = datetime.timedelta(hours = 19)

    if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé à l'horaire spécifié"))}), 404

    conn = connect_pg.connect()
    query = f"select NbrHeureSemestre from edt.ressource where idRessource = {json_data['idRessource']}" # vérifier si il reste assez d'heures
    try:
        NbrHeureSemestre = str(connect_pg.get_query(conn, query)[0][0])
        if(NbrHeureSemestre == '0'):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Plus aucune heures est disponible pour la ressource spécifié"))}), 400
        
        NbrHeureSemestre = datetime.timedelta(seconds = int(NbrHeureSemestre) )
        NombreHeure = datetime.timedelta(hours = int(json_data['NombreHeure'][:2]),minutes = int(json_data['NombreHeure'][3:5]))

        if (NbrHeureSemestre - NombreHeure) < datetime.timedelta(hours = 00,minutes = 00)  :
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = f"La ressource spécifié ne possède pas le nombre d'heures demandé"))}), 400
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_data['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "récupérer"))}), 500


    query = f"Insert into edt.cours (HeureDebut, NombreHeure, Jour, idRessource, typeCours) values ('{json_data['HeureDebut']}', '{json_data['NombreHeure']}', '{json_data['Jour']}', '{json_data['idRessource']}', '{json_data['typeCours']}') returning idCours"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_data['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("cours"))}), 500
    query = f"update edt.ressource set nbrheuresemestre = '{(int((NbrHeureSemestre - NombreHeure).total_seconds()))}'   where idRessource = {json_data['idRessource']}" # pour mettre à jour le nombre d'heures
    
    try:
        connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_data['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("ressource", "mettre à jour"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement) 


@cours.route('/cours/getProfCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_prof_cours(idCours):
    """Renvoit l'enseignant d'un cours via la route /cours/getProfCours/<idCours>
    
    :param idCours: id du cours
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    :raises ParamètreTypeInvalideException: Si le type du paramètre d'entrée idCours n'est pas valide
    
    :return: l'id du cours
    :rtype: flask.wrappers.Response(json)
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    query = f"select edt.professeur.* from edt.professeur inner join edt.enseigner using(idProf) inner join edt.cours as e1 using(idCours) where e1.idCours = {idCours}"
    returnStatement = []
    conn = connect_pg.connect()

    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Cours, Enseigner ou Professeur",idCours))}), 400
        for row in rows:
            returnStatement.append(get_professeur_statement(row))
    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("Cours, Enseigner et Professeur", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/enleverProf/<idCours>', methods=['DELETE'])
@jwt_required()
def enlever_Prof(idCours):
    """Permet d'enlever un enseignant assigner à un cours via la route /cours/enleverProf/<idCours>
    
    :param idCours: id du cours
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si la clée spécifié pour la colonne idCours n'a pas pu être trouvé
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la suppression

    :return: id du cours supprimer
    :rtype: flask.wrappers.Response(String)
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    query = f"delete from edt.enseigner where idCours={idCours}"
    conn = connect_pg.connect()
    try:
        connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Enseigner ", idCours))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("Enseigner","supprimer"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(idCours)


@cours.route('/cours/ajouterGroupe/<idCours>', methods=['POST', 'PUT'])
@jwt_required()
def ajouter_groupe(idCours):
    """Permet d'ajouter un cours à un groupe via la route /cours/ajouterGroupe/<idCours>
    
    :param idCours: id du cours qui doit recevoir 
    :type idCours: int

    :param idGroupe: id du groupe à ajouter au cours spécifié dans le body
    :type idGroupe: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours ou idGroupe est invalide, une valeur numérique est attendue
    :raises DonneeIntrouvableException: Si une des clées n'a pas pu être trouvé
    :raises ActionImpossibleException: Impossible de réaliser l'insertion
    :raises ParamètreInvalideException: Si le groupe n'est pas disponible à l'horaire spécifié

    :return: id du groupe
    :rtype: flask.wrappers.Response(json)
    """
    conn = connect_pg.connect()
    json_data = request.get_json()

    if 'idGroupe' not in json_data :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400

    if (not idCours.isdigit() or type(json_data['idGroupe']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idGroupe", "numérique"))}), 400
    
    courGroupe = get_cours(str(idCours))
    if type(courGroupe) == tuple :
        return jsonify({'error': str(apiException.ActionImpossibleException("cours"))}), 500

    courGroupe = json.loads(get_cours(str(idCours)).data) 
    HeureDebut = courGroupe['HeureDebut']
    NombreHeure = courGroupe['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
    HeureFin = str(HeureDebut + NombreHeure)

    query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.etudier using(idCours)  where idGroupe = {json_data['idGroupe']}
    and ((HeureDebut <= '{courGroupe['HeureDebut']}' and '{courGroupe['HeureDebut']}'::time <=  (HeureDebut + NombreHeure::interval))
    or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
    and ('{courGroupe['Jour']}' = Jour and idCours is not null) order by idCours asc
    """

    result = connect_pg.get_query(conn , query)
    
    if result != []:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce groupe n'est pas disponible à la période spécifié"))}), 400
    
    returnStatement = {}
    query = f"Insert into edt.etudier (idGroupe, idCours) values ('{json_data['idGroupe']}', '{idCours}') returning idCours"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "cours" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Groupe ", json_data['idGroupe']))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idGroupe = {json_data['idGroupe']} et idCours = {idCours}"
            messageColonne = f"idGroupe et idCours"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "Etudier"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("Etudier"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/getAllCoursType/', methods=['GET','POST'])
@jwt_required()
def get_all_cours_type():
    """Renvoit tous les types de cours via la route /cours/getAllCoursType/
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    
    :return: tous les types de cours
    :rtype: flask.wrappers.Response(json)
    """
    query = f"SELECT e.enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'typecours' "

    conn = connect_pg.connect()
    try:
        rows = connect_pg.get_query(conn, query)
        print('---------------')
        print(rows)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("TypeCours"))}), 404
    except Exception as e:
        return jsonify({'erreur': str(apiException.ActionImpossibleException("TypeCours", "récupérer"))}), 500
    return jsonify(rows)