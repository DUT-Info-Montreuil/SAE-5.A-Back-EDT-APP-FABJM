from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.cours_service import get_cours_statement, getCoursProf, getCoursGroupeService
from src.services.user_service import get_professeur_statement

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

@cours.route('/cours/get/<filtre>', methods=['GET','POST'])
@jwt_required()
def get_cours(filtre):
    """Renvoit les cours remplisant les critères d'un filtre spécifié par son via la route /cours/get/<filtre>
    
    :param filtre: peut-être l'id du cours ou un jour au format aaaa-mm-jj, si le filtre == "null" aucun filtre est appliqué
    :type filtre: str, int
    
    :raises ParamètreInvalideException: Le paramètre filtre est invalide
    :raises AucuneDonneeTrouverException: Aucune donnée n'a pas être trouvé correspont aux critère
    :raises ActionImpossibleException: Si une erreur est survenue de la récupération des données
    
    :return: Les cours filtrés
    :rtype: json
    """

    conn = connect_pg.connect()
    if(perm.getUserPermission(get_jwt_identity() , conn) == 2):
        rows = getCoursProf(get_jwt_identity() , conn)
        returnStatement = []
        try:
            for row in rows:
                returnStatement.append(get_cours_statement(row))
        except(TypeError) as e:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    
    elif(perm.getUserPermission(get_jwt_identity() , conn) == 3):
        idGroupe = connect_pg.get_query(conn , f"select idGroupe from edt.eleve where idUtilisateur ={get_jwt_identity()}")[0][0]
        rows = getCoursGroupeService(idGroupe , conn)
        returnStatement = []
        try:
            for row in rows:
                returnStatement.append(get_cours_statement(row))
        except(TypeError) as e:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("cours"))}), 404
        connect_pg.disconnect(conn)
        return jsonify(returnStatement)
    if filtre.isdigit():
        query = f"select * from edt.cours where idCours='{filtre}'"

    elif len(filtre) == 10 and len(filtre.split("-")) == 3 : 
        query = f"select * from edt.cours where jour='{filtre}'"

    elif filtre == "null":
        query = f"select * from edt.cours"

    else:
        return jsonify({'error': str(apiException.ParamètreInvalideException("filtre"))}), 400

    
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    if rows == []:
        return jsonify({'error': str(apiException.AucuneDonneeTrouverException("Cours"))}), 400
    try:
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
    :raises InsertionImpossibleException: Si une erreur inconnue survient durant la récupération des données
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """
    returnStatement = []
    conn = connect_pg.connect()
    try:
        rows = getCoursGroupeService(idGroupe , conn)
        if rows == []:
            return jsonify({'erreur': str(apiException.DonneeIntrouvableException("Etudier",idGroupe))}), 400
        for row in rows:
            returnStatement.append(get_cours_statement(row))
    except Exception as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("Cours, Etudier et Groupe", "récupérer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@cours.route('/cours/deplacer/<idCours>', methods=['PUT'])
@jwt_required()
def deplacer_cours(idCours):
    """Permet de déplacer un cours via la route /cours/deplacer/<idCours>
    
    :param idCours: id du cours à déplacer
    :type idCours: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours déplacer si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    json_datas = request.get_json()
    
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
    
@cours.route('/cours/modifierCours/<idCours>', methods=['PUT'])
@jwt_required()
def modifier_cours(idCours):
    """Permet de modifier un cours via la route /cours/deplacer/<idCours>
    
    :param idCours: id du cours à modifier
    :type idCours: int

    :param NombreHeure: NombreHeure à modifier spécifié dans le body si le cas
    :type NombreHeure: int

    :param idRessource: idRessource à modifier spécifié dans le body si le cas
    :type idRessource: int

    :raises ParamètreBodyManquantException: Si aucun paramètre d'entrée attendu n'est spécifié dans le body
    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours modifier si présent
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    json_datas = request.get_json()
    cour = get_cours(idCours)
    
    if 'NombreHeure' not in json_datas and 'idRessource' not in json_datas:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    else:
        query = "UPDATE edt.cours "
        if 'NombreHeure' in json_datas:
            query += f"SET NombreHeure = '{json_datas['NombreHeure']}'"
        if 'idRessource' in json_datas:
            if 'NombreHeure' in json_datas:
                query += f" , idRessource = '{json_datas['idRessource']}'"
            else:
                query += f"SET idRessource = '{json_datas['idRessource']}'"
        query += f" where idCours={idCours}"

        conn = connect_pg.connect()
        
        try:
            returnStatement = connect_pg.execute_commands(conn, query)
        except Exception as e:
            if e.pgcode == "23503":# violation contrainte clée étrangère
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours"))}), 400
            
            else:
                # Erreur inconnue
                return jsonify({'error': str(apiException.InsertionImpossibleException("enseigner"))}), 500
        
   
        
        if type(cour) != tuple : 
            cour = json.loads(cour.data)
            aujourdhui = date.today()
            jourCours = date(int(cour[0]['Jour'][:4]), int(cour[0]['Jour'][5:7]), int(cour[0]['Jour'][8:10]))
            HeureDebut = datetime.timedelta(hours = int(cour[0]['HeureDebut'][:2]),minutes = int(cour[0]['HeureDebut'][3:5]), seconds = 00)
            HeureActuelle = str(datetime.datetime.now())
            HeureActuelle = datetime.timedelta(hours = int(HeureActuelle[11:13]),minutes = int(HeureActuelle[14:16]), seconds = 00)
            
            if( jourCours > aujourdhui  or (jourCours == aujourdhui and HeureDebut > HeureActuelle)):
                if ('NombreHeure' in json_datas and json_datas['NombreHeure'] != cour[0]['NombreHeure']) and ('idRessource' not in json_datas or json_datas['idRessource'] == cour[0]['idRessource']): # Si le nombreHeure a changé mais toujours dans la même ressource
                    query = f"update edt.ressource set nbrheuresemestre =  ((nbrheuresemestre + '{cour[0]['NombreHeure']}') - '{json_datas['NombreHeure']}' )  where idRessource = {cour[0]['idRessource']}" # pour mettre à jour le nombre d'heures
                
                elif ('NombreHeure' not in json_datas or json_datas['NombreHeure'] == cour[0]['NombreHeure']) and ('idRessource' in json_datas and json_datas['idRessource'] != cour[0]['idRessource']): # Si le nombreHeure est inchangé mais que ce n'est plus la même ressource
                    query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + '{cour[0]['NombreHeure']}')  where idRessource = {cour[0]['idRessource']}" 
                    query2 = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre - '{cour[0]['NombreHeure']}')  where idRessource = {json_datas['idRessource']}" 
                    connect_pg.execute_commands(conn, query2)
                
                elif ('NombreHeure' in json_datas and json_datas['NombreHeure'] != cour[0]['NombreHeure']) and  ('idRessource' in json_datas and json_datas['idRessource'] != cour[0]['idRessource']): # Si le nombreHeure a changé et que ce n'est plus la même ressource
                    query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + '{cour[0]['NombreHeure']}')  where idRessource = {cour[0]['idRessource']}" 
                    query2 = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre - '{json_datas['NombreHeure']}')  where idRessource = {json_datas['idRessource']}" 
                    connect_pg.execute_commands(conn, query2)

                try:
                    connect_pg.execute_commands(conn, query)
                    if query2:
                        connect_pg.execute_commands(conn, query2)
                except psycopg2.IntegrityError as e:
                    if e.pgcode == '23503':
                        # Erreur violation de contrainte clée étrangère de la table Ressources
                        return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", cour[0]['idRessource']))}), 400
                    else:
                        # Erreur inconnue
                        return jsonify({'error': str(apiException.InsertionImpossibleException("ressource", "mettre à jour"))}), 500
                        
        
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
    :raises InsertionImpossibleException: Impossible de réaliser l'insertion

    :return: id du cours
    :rtype: int
    """
    json_datas = request.get_json()
    
    if 'idProf' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    
    if (not idCours.isdigit() or type(json_datas['idProf']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours ou idProf", "numérique"))}), 400
    
    returnStatement = {}
    conn = connect_pg.connect()

    courGroupe = get_cours(idCours)
    if type(courGroupe) != tuple :
        cour = json.loads(get_cours(idCours).data) 

        HeureDebut = cour[0]['HeureDebut']
        NombreHeure = cour[0]['NombreHeure']
        HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00 )
        NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00 )
        HeureFin = str(HeureDebut + NombreHeure)

        query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.enseigner using(idCours)  where idProf = {json_datas['idProf']}
        and ((HeureDebut <= '{cour[0]['HeureDebut']}' and '{cour[0]['HeureDebut']}'::time <=  (HeureDebut + NombreHeure::interval))
        or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
        and ('{cour[0]['Jour']}' = Jour and idCours is not null) order by idCours asc
        """
        result = connect_pg.get_query(conn , query)
        if result != []:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Ce professeur n'est pas disponible à la période spécifié"))}), 400

    query = f"Insert into edt.enseigner (idProf, idCours) values ('{json_datas['idProf']}', '{idCours}') returning idCours"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except Exception as e:
        if e.pgcode == "23503":# violation contrainte clée étrangère
            if "prof" in str(e):
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Professeur ", json_datas['idProf']))}), 400
            else:
                return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours ", idCours))}), 400
        
        elif e.pgcode == "23505": # si existe déjà
            messageId = f"idCours = {idCours} et idProf = {json_datas['idProf']}"
            messageColonne = f"idCours et idProf"
            return jsonify({'error': str(apiException.DonneeExistanteException(messageId, messageColonne, "enseigner"))}), 400
        
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("enseigner"))}), 500

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
    :raises InsertionImpossibleException: Impossible de réaliser l'insertion

    :return: id du cours supprimer si présent
    :rtype: json
    """
    json_datas = request.get_json()
    if (not idCours.isdigit() or type(json_datas['idSalle']) != int   ):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400
    
    
    if 'idSalle' not in json_datas :
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    conn = connect_pg.connect()
    coursSalle = get_cours(idCours)
    
    if type(coursSalle) != tuple:
        coursSalle = json.loads(get_cours(idCours).data) 

        HeureDebut = coursSalle[0]['HeureDebut']
        NombreHeure = coursSalle[0]['NombreHeure']
        HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = 00)
        NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
        HeureFin = str(HeureDebut + NombreHeure)

        query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.accuellir using(idCours)  where idSalle = {json_datas['idSalle']}
        and ((HeureDebut <= '{coursSalle[0]['HeureDebut']}' and '{coursSalle[0]['HeureDebut']}'::time <=  (HeureDebut + NombreHeure::interval))
        or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
        and ('{coursSalle[0]['Jour']}' = Jour and idCours is not null) order by idCours asc
        """

        result = connect_pg.get_query(conn , query)
        if result != []:
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Cette salle n'est pas disponible à l'horaire spécifié"))}), 400
        
    
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
            return jsonify({'error': str(apiException.InsertionImpossibleException("accuellir"))}), 500

    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@cours.route('/cours/removeSalle/<idCours>', methods=['DELETE'])
@jwt_required()
def remove_salle(idCours):
    """Permet de supprimer une salle attribuer à un cours via la route /cours/deleteSalle/<idCours>
    
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
    """Permet de supprimer un cours via la route /cours/delete/<idCours>, si le cours n'a pas encore eu lieu les heures de la ressource sont restaurés
    
    :param idCours: id du cours à supprimer
    :type idCours: int

    :raises ParamètreTypeInvalideException: Le type de idCours est invalide, une valeur numérique est attendue

    :return: id du cours supprimer si présent
    :rtype: json
    """

    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "numérique"))}), 400

    conn = connect_pg.connect() 
    cour = get_cours(idCours)

    if type(cour) != tuple : 
        cour = json.loads(get_cours(idCours).data)
        aujourdhui = date.today()
        jourCours = date(int(cour[0]['Jour'][:4]), int(cour[0]['Jour'][5:7]), int(cour[0]['Jour'][8:10]))
        HeureDebut = datetime.timedelta(hours = int(cour[0]['HeureDebut'][:2]),minutes = int(cour[0]['HeureDebut'][3:5]), seconds = 00)
        HeureActuelle = str(datetime.datetime.now())
        HeureActuelle = datetime.timedelta(hours = int(HeureActuelle[11:13]),minutes = int(HeureActuelle[14:16]), seconds = 00)

        if( jourCours > aujourdhui  or (jourCours == aujourdhui and HeureDebut > HeureActuelle)):
            query = f"update edt.ressource set nbrheuresemestre =  (nbrheuresemestre + '{cour[0]['NombreHeure']}')  where idRessource = {cour[0]['idRessource']}" # pour mettre à jour le nombre d'heures
            try:
                connect_pg.execute_commands(conn, query)
            except psycopg2.IntegrityError as e:
                if e.pgcode == '23503':
                    # Erreur violation de contrainte clée étrangère de la table Ressources
                    return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", cour[0]['idRessource']))}), 400
                else:
                    # Erreur inconnue
                    return jsonify({'error': str(apiException.InsertionImpossibleException("ressource", "mettre à jour"))}), 500
    
    query = f"delete from edt.cours where idCours = {idCours}"
    try:
        connect_pg.execute_commands(conn, query)

    except psycopg2.IntegrityError as e:
        print("Erreur : ", e)
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Cours
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Cours", idCours))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("Cours", "supprimer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(idCours)
    

@cours.route('/cours/add', methods=['POST'])
@jwt_required()
def add_cours():
    """Permet d'ajouter un cours via la route /cours/add
    
    :param cours: donnée représentant un cours spécifié dans le body
    :type cours: json
    
    :raises InsertionImpossibleException: Impossible d'ajouter le cours spécifié dans la table cours
    :raises DonneeIntrouvableException: La valeur de la clée étrangère idRessource n'a pas pu être trouvé
    :raises ParamètreBodyManquantException: Si ou plusieurs paramètres sont manquant dans le body
    :raises ParamètreInvalideException: Si ou plusieurs paramètres sont incohérent ou invalide
    
    
    :return: le cours qui vient d'être créé
    :rtype: json
    """
    json_datas = request.get_json()
    if 'HeureDebut' not in json_datas or 'NombreHeure' not in json_datas or 'Jour' not in json_datas or 'idRessource' not in json_datas:
        return jsonify({'error': str(apiException.ParamètreBodyManquantException())}), 400
    
    if not verif.estDeTypeTime(json_datas['HeureDebut']) or not verif.estDeTypeTimeStamp(json_datas['Jour']) or not verif.estDeTypeTime(json_datas['NombreHeure']) or type(json_datas['NombreHeure']) == int:
        return jsonify({'error': str(apiException.ParamètreInvalideException("HeureDebut, NombreHeure, idRessource ou Jour"))}), 404


    HeureDebut = json_datas['HeureDebut']
    NombreHeure = json_datas['NombreHeure']
    HeureDebut = datetime.timedelta(hours = int(HeureDebut[:2]),minutes = int(HeureDebut[3:5]), seconds = int(HeureDebut[6:8]))
    NombreHeure = datetime.timedelta(hours = int(NombreHeure[:2]),minutes = int(NombreHeure[3:5]), seconds = 00)
    HeureFin = HeureDebut + NombreHeure

    heure_ouverture_iut = datetime.timedelta(hours = 8)
    heure_fermeture_iut = datetime.timedelta(hours = 19)

    if HeureDebut < heure_ouverture_iut or HeureFin > heure_fermeture_iut:
        return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "L'iut est fermé à l'horaire spécifié"))}), 404

    conn = connect_pg.connect()
    query = f"select NbrHeureSemestre from edt.ressource where idRessource = {json_datas['idRessource']}" # vérifier si il reste assez d'heures
    try:
        NbrHeureSemestre = str(connect_pg.get_query(conn, query)[0][0])
        if(NbrHeureSemestre == '00:00:00'):
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = "Plus aucune heures est disponible pour la ressource spécifié"))}), 400
        
        NbrHeureSemestre = datetime.timedelta(hours = int(NbrHeureSemestre[:2]),minutes = int(NbrHeureSemestre[3:5]))
        NombreHeure = datetime.timedelta(hours = int(json_datas['NombreHeure'][:2]),minutes = int(json_datas['NombreHeure'][3:5]))

        if (NbrHeureSemestre - NombreHeure) < datetime.timedelta(hours = 00,minutes = 00)  :
            return jsonify({'error': str(apiException.ParamètreInvalideException(None, message = f"La ressource spécifié ne possède pas le nombre d'heures demandé"))}), 400
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_datas['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("ressource", "récupérer"))}), 500


    query = f"Insert into edt.cours (HeureDebut, NombreHeure, Jour, idRessource) values ('{json_datas['HeureDebut']}', '{json_datas['NombreHeure']}', '{json_datas['Jour']}', '{json_datas['idRessource']}') returning idCours"
    
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_datas['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("cours"))}), 500
        
    
    query = f"update edt.ressource set nbrheuresemestre = '{str(NbrHeureSemestre - NombreHeure)}'  where idRessource = {json_datas['idRessource']}" # pour mettre à jour le nombre d'heures
    
    try:
        connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23503':
            # Erreur violation de contrainte clée étrangère de la table Ressources
            return jsonify({'error': str(apiException.DonneeIntrouvableException("Ressources", json_datas['idRessource']))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.InsertionImpossibleException("ressource", "mettre à jour"))}), 500
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement) #



@cours.route('/cours/getProfCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_prof_cours(idCours):
    """Renvoit l'enseignant d'un cours via la route /cours/getProfCours/<idCours>
    
    :param idCours: id du cours
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises InsertionImpossibleException: Si une erreur inconnue survient durant la récupération des données
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
        return jsonify({'erreur': str(apiException.InsertionImpossibleException("Cours, Enseigner et Professeur", "récupérer"))}), 500
        
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