
import pytest
from src.rest_api import create_app, init_bdd
import sqlite3
import json
import os

@pytest.fixture()
def client(request):
    """Créer une instance permet de simuler des requêtes HTTP vers une application Flask et de tester son comportement
    et intégrant une base de donnée virtuelle

    :param request: Pour recevoir les arguments du test pour paramétrer les données
    :type request: SubRequest
    :return: l'instance de test
    :rtype: FlaskClient
    """
    # Paramétrage des données de test
    test_data = getattr(request, "param", None)  # Recevoir les arguments du test pour les données
    db_conn = sqlite3.connect(':memory:')
    app = create_app({'TESTING': True, 'DATABASE': db_conn})

    
    with app.test_client() as client:
        init_bdd(db_conn, os.getcwd()+"/database/SQL_script/commands.sql")
        insert_bdd(db_conn, test_data)
        yield client
        fermer_bdd(db_conn)

# Ajoutez un paramètre supplémentaire à insert_bdd pour recevoir des données de test
def insert_bdd(db_conn, test_data):
    """Insert des données de base nécessaire au tests dans la base de donnée 

    :param db_conn: une connection à une base de donnée
    :type db_conn: connection
    :param test_data: Les données de test à insérer
    :type test_data: dict
    """
    db_cursor = db_conn.cursor()
    if test_data and test_data.get('utilisateur'):
        db_cursor.execute("INSERT INTO Utilisateur (idUtilisateur,FirstName, LastName, Username, Password) VALUES (?, ?, ?, ?, ?)", test_data['utilisateur'])
        db_cursor.execute("INSERT INTO Admin (idUtilisateur) VALUES (?)", (test_data['utilisateur'][0],))
    db_conn.commit()


def login(client, username,password):
    """Permet de s'authentifier au près de JWT

    :param client: une instance de test
    :type client: FlaskClient
    """
    login_data = {'Username': username, 'Password': password}
    response = client.post('/utilisateurs/auth', data=json.dumps(login_data), content_type='application/json', follow_redirects=True)
    token = response.json['accessToken']
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'

def fermer_bdd(db_conn):
    """Ferme la connection à la base de donnée

    :param db_conn: une connection à une base de donnée
    :type db_conn: Connexion
    """
    db_conn.close()





