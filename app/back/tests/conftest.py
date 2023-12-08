import os
import tempfile
import pytest
import json
from flask import jsonify
from src.rest_api import create_app
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta

import requests



#["accessToken"]
@pytest.fixture
def client():
    
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        with app.app_context():
            # Spécifiez le chemin de votre fichier SQL
            sql_file_path = os.path.dirname(os.path.dirname(os.getcwd())) + "/database/SQL_script/commands.sql"
            # Exécutez le fichier SQL
            #execute_sql_file(app.db, sql_file_path)
            
            secret_key = os.urandom(32)
            app.config['SECRET_KEY'] = secret_key
            app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
            #token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMTk5MDk2OSwianRpIjoiNjIyYTQ1N2QtNjQzOS00ZTI3LWI5NjctMmM1ODY1ODBlOTFiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Im1vbm9rdW1hIiwibmJmIjoxNzAxOTkwOTY5LCJleHAiOjE3MDE5OTE4Njl9.oP1LKpN8pWgmxpmds0nARL7j5jObDsdE5hBzTp2tQyA"
            
            data = {'Username': 'monokuma', 'PassWord': 'despair'}
            headers = {'Content-Type': 'application/json'}
            resp = client.get('/utilisateurs/auth', data=json.dumps(data), headers=headers)
            data = resp.data
            print(resp.status_code)
            print(resp.headers['Content-Type'])# == 'application/json'
            token = json.loads(resp.data)['accessToken']
            print(token)
            app.headers = {'Authorization': f'Bearer {token}'}

        
        #tab = (client.get('/utilisateurs/auth').data.decode())[0]
        
        yield client
    #print("try : ", client.get('/utilisateurs/auth').data)
    
    os.close(db_fd)
    os.unlink(db_path)


# Ajoutez cette fonction pour lire et exécuter le fichier SQL
def execute_sql_file(db, sql_file_path):
    with open(sql_file_path, 'r') as sql_file:
        sql_script = sql_file.read()
        with db.cursor() as cursor:
            cursor.execute(sql_script)
        db.commit()

