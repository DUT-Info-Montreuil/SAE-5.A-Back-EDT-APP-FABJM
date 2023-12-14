#!/usr/bin/python

import psycopg2
from src.config import config


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
        params = config(filename, section)

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        conn.set_client_encoding('UTF8')

        # create a cursor
        cur = conn.cursor()

        # execute a statement   
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
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
    conn.close()
    print('Database connection closed.')


def execute_commands(conn, commands):
    """Execute la commande sql

    :param conn: objet représentant la connection à la base de donnée
    :type conn: psycopg2.extensions.connection
    
    :param commands: commande sql
    :type commands: String
    
    :return:  si il y a une valeur de retour de la commande
    :rtype: Boolean
    """
    cur = conn.cursor()

    returningValue = False

    # create table one by one
    cur.execute(commands)
    if " returning " in commands.lower():
            returningValue = cur.fetchone()[0]
            # commit the changes
    conn.commit()
    # close communication with the PostgreSQL database server
    cur.close()
    if returningValue:
        return returningValue


def get_query(conn, query):
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
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
    finally:
        if conn is not None:
            return rows


if __name__ == '__main__':
    connect()