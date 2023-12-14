
import pytest
from src.rest_api import create_app, init_bdd
import sqlite3
import json


@pytest.fixture()
def client():
    """Créer une instance permet de simuler des requêtes HTTP vers une application Flask et de tester son comportement
    et intégrant une base de donnée virtuelle

    :return: l'instance de test
    :rtype: FlaskClient
    """
    db_conn = sqlite3.connect(':memory:')
    app = create_app({'TESTING': True, 'DATABASE': db_conn})
    with app.test_client() as client:
        init_bdd(db_conn, "/database/SQL_script/commands.sql")
        insert_bdd(db_conn)
        yield client
        fermer_bdd(db_conn)

def insert_bdd(db_conn):
    """Insert des données nécessaire au tests dans la base de donnée 

    :param db_conn: une connection à une base de donnée
    :type db_conn: connection
    """
    db_cursor = db_conn.cursor()
    db_cursor.execute("INSERT INTO Utilisateur (idUtilisateur,FirstName, LastName, Username, Password) VALUES (1,'John', 'Doe', 'johndoe', 'password123')")
    db_cursor.execute("INSERT INTO Admin (idUtilisateur) VALUES (1)")
    db_conn.commit()


def login(client):
    """Permet de s'authentifier au près de JWT

    :param client: une instance de test
    :type client: FlaskClient
    """
    login_data = {'Username': 'johndoe', 'Password': 'password123'}
    response = client.get('/utilisateurs/auth', data=json.dumps(login_data), content_type='application/json', follow_redirects=True)
    token = response.json['accessToken']
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'

def fermer_bdd(db_conn):
    """Ferme la connection à la base de donnée

    :param db_conn: une connection à une base de donnée
    :type db_conn: Connexion
    """
    db_conn.close()





