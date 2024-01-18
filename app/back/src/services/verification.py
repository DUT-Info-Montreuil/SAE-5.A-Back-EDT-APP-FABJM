# -*- coding: utf-8 -*-
# verification.py

import json
from flask import jsonify
import src.apiException as apiException
import src.connect_pg as connect_pg

def estDeTypeTime(string):
    """Détermine si un string respecte le format time (sql) hh:mm:ss

    :param string: Prends en paramètre d'entrée une chaine de string
    :type string: String
    
    :return: Retourne True si le string est un time, False sinon
    :rtype: bool
    """
    if len(string) != 8:
        return False
    try:
        for k in range(0,1):
            if not string[k].isdigit():
                return False

        if string[2] != ":":
            return False

        for k in range(3,4):
            if not string[k].isdigit():
                return False

        if string[5] != ":":
            return False

        for k in range(6,7):
            if not string[k].isdigit():
                return False

        return True
    
    except IndexError:
        return False

def estDeTypeDate(string):
    """Détermine si un string respecte le format DATE (sql) yyyy-mm-jj

    :param string: Prends en paramètre d'entrée une chaine de string
    :type string: String
    
    :return: Retourne True si le string est un DATE, False sinon
    :rtype: bool
    """
    if len(string) != 10:
        return False

    try :
        for k in range(0,3):
            if not string[k].isdigit():
                return False

        if string[4] != "-":
            return False

        for k in range(5,6):
            if not string[k].isdigit():
                return False

        if string[7] != "-":
            return False

        for k in range(8,9):
            if not string[k].isdigit():
                return False

        return True
    except IndexError:
        return False
    
def groupeEstDispo(idGroupe, HeureDebut, HeureFin, Jour, conn, idCours):
    """Détermine si un groupe est disponible à l'horaire définie

    :param idGroupe: L'id d'un groupe
    :type idGroupe: int

    :param HeureDebut: L'heure de début de la période au format time hh:mm:ss
    :type HeureDebut: String

    :param HeureFin: L'heure de fin de la période au format time hh:mm:ss
    :type HeureFin: String

    :param Jour: Le jour de la période au format time hh:mm:ss
    :type Jour: String

    :param conn: Une connection à une base de donnée
    :type conn: psycopg2.extensions.connection
    
    :return: Retourne True si le groupe est disponible, False sinon
    :rtype: bool
    """

    query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.etudier using(idCours)  where idGroupe = {idGroupe} and idCours != {idCours}
    and ((HeureDebut <= '{HeureDebut}' and '{HeureDebut}'::time <=  (HeureDebut + NombreHeure::interval))
    or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
    and ('{Jour}' = Jour and idCours is not null) order by idCours asc
    """

    result = connect_pg.get_query(conn , query)
    
    if result != []:
        return False
    else:
        return True
    

def profEstDispo(idProf, HeureDebut, HeureFin, Jour, conn, idCours):
    """Détermine si un enseignant est disponible à l'horaire définie

    :param idGroupe: L'id d'un groupe
    :type idGroupe: int

    :param HeureDebut: L'heure de début de la période au format time hh:mm:ss
    :type HeureDebut: String

    :param HeureFin: L'heure de fin de la période au format time hh:mm:ss
    :type HeureFin: String

    :param Jour: Le jour de la période au format time hh:mm:ss
    :type Jour: String

    :param conn: Une connection à une base de donnée
    :type conn: psycopg2.extensions.connection
    
    :return: Retourne True si le groupe est disponible, False sinon
    :rtype: bool
    """
    query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.enseigner using(idCours)  where idProf = {idProf} and idCours != {idCours}
    and ((HeureDebut <= '{HeureDebut}' and '{HeureDebut}'::time <=  (HeureDebut + NombreHeure::interval))
    or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
    and ('{Jour}' = Jour and idCours is not null) order by idCours asc
    """
    result = connect_pg.get_query(conn , query)
    if result != []:
        return False
    else:
        return True




def salleEstDispo(idSalle, HeureDebut, HeureFin, Jour, conn, idCours):
    """Détermine si une salle est disponible à l'horaire définie

    :param idGroupe: L'id d'un groupe
    :type idGroupe: int

    :param HeureDebut: L'heure de début de la période au format time hh:mm:ss
    :type HeureDebut: String

    :param HeureFin: L'heure de fin de la période au format time hh:mm:ss
    :type HeureFin: String

    :param Jour: Le jour de la période au format time hh:mm:ss
    :type Jour: String

    :param conn: Une connection à une base de donnée
    :type conn: psycopg2.extensions.connection
    
    :return: Retourne True si le groupe est disponible, False sinon
    :rtype: bool
    """ 
    query = f"""SELECT edt.cours.* FROM edt.cours inner join edt.accuellir using(idCours)  where idSalle = {idSalle} and idCours != {idCours}
    and ((HeureDebut <= '{HeureDebut}' and '{HeureDebut}'::time <=  (HeureDebut + NombreHeure::interval))
    or ( HeureDebut <= '{HeureFin}' and '{HeureFin}'::time <= (HeureDebut + NombreHeure::interval)))
    and ('{Jour}' = Jour and idCours is not null) order by idCours asc
    """

    result = connect_pg.get_query(conn , query)
    if result != []:
        return False
    else:
        return True