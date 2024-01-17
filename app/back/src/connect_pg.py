#!/usr/bin/python

import psycopg2
from src.config import config
import flask

app = flask.current_app

def connect(filename='./app/back/src/config.ini', section='postgresql'):
    """Établit la connection à la base de donnée

    :param filename: chemin vers le fichier de configuration, par défaut config.ini
    :type filename: String, optionnel
    
    :param section: nom de la section à rechercher, par défaut postgresql
    :type section: String, optionnel
    
    :raises Exception: Une erreur est survenue lors de l'éxécution de la fonction
    :raises psycopg2.DatabaseError: Une erreur liée à la base de données est survenue
    
    :return: un objet représentant la connection à la base de donnée
    :rtype: psycopg2.extensions.connection
    """
    conn = None
    
    try:
        # read connection parameters
        print('Connecting to the database...')
        
        if app.config['TESTING']:
            conn = app.config['DATABASE']
        else:
            params = config(filename, section)
            conn = psycopg2.connect(**params)

        cur = conn.cursor()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
    finally:
        if conn is not None:
            return conn


def disconnect(conn):
    """ferme la connection à la base de donnée

    :param conn: objet représentant la connection à la base de donnée
    :type conn: psycopg2.extensions.connection
    """
    if not app.config['TESTING']:
        conn.close()
        print('Database connection closed.')


def execute_commands(conn, commands, param=""):
    """Execute la commande sql

    :param conn: objet représentant la connection à la base de donnée
    :type conn: psycopg2.extensions.connection
    
    :param commands: commande sql
    :type commands: String
    
    :return: Une valeur de retour de la requete
    :rtype: int
    """
    cur = conn.cursor()

    returningValue = False

    # create table one by one
    if app.config['TESTING']:
        query, returningValue = formatageSqlite3(commands)
        cur.execute(query)
        conn.commit()
        cur.close()
        if returningValue:
            return cur.lastrowid

    else:
        cur.execute(commands, param)
        if " returning " in commands.lower():
            returningValue = cur.fetchone()[0] # TODO: change to permit multiple value return
            # commit the changes
        conn.commit()
        # close communication with the PostgreSQL database server
        cur.close()
        if returningValue:
            return returningValue


def get_query(conn, query, param=""):
    """Récupère les données dans la base de donnée

    :param conn: objet représentant la connection à la base de donnée
    :type conn: psycopg2.extensions.connection
    
    :param query: requete sql
    :type query: String
    
    :raises Exception: Une erreur est survenue lors de l'éxécution de la fonction
    :raises psycopg2.DatabaseError: Une erreur liée à la base de données est survenue
    
    :return:  la valeur souhaité
    :rtype: tableau
    """
    if app.config['TESTING']:
        query = formatageSqlite3(query)[0]

    try:
        cur = conn.cursor()
        if param != "":
            cur.execute(query, param)
        else:
            cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
    finally:
        if conn is not None:
            try:
                return rows
            except UnboundLocalError:
                return []

def formatageSqlite3(phrase):
    """Transforme une requête posgresql en sqlite3

    :param phrase: requete posgresql
    :type phrase: str

    :return: une requete au format sqlite3
    :rtype: str

    :return: Si une valeur de retour est attendue
    :rtype: bool
    """
    nouvelle_phrase = ''
    if 'EDT' in phrase:
        return nouvelle_phrase, False
    for lettre in phrase.split(" "):
        if lettre[:4] == 'edt.':
            nouvelle_phrase += lettre[4:] + " "
        elif lettre == "cascade;\n":
            nouvelle_phrase += ";\n"
        elif lettre == "SERIAL,\n":
            nouvelle_phrase += "int AUTO_INCREMENT,\n"
        elif lettre == 'returning':
            return nouvelle_phrase, True
        else:
            nouvelle_phrase += lettre + " "
    return nouvelle_phrase, False


if __name__ == '__main__':
    connect()