import pytest
import requests


from conftest import client, login 

API_URL = 'http://localhost:5050'
TOKEN = None


"""
'/utilisateurs/auth'
"""
#utilisateur existant
jeuDeDonnees = [({'utilisateur': (1, 'John', 'Doe', 'johndoe', 'password123')})]
@pytest.mark.parametrize('client', jeuDeDonnees, indirect=True)
def test_auth_existant(client):
    """Teste l'authentification d'un utilisateur existant

    :param client: une instance de test
    :type client: FlaskClient
    """
    body = {
        "Username" : "johndoe",
        "Password" : "password123"
    }
    headers = {'Content-Type': 'application/json'}
    response = client.post('/utilisateurs/auth', json=body, headers=headers)

    assert response.status_code == 200
    assert 'accessToken' in response.json
    assert 'firstLogin' in response.json
    
#utilisateur inexistant
jeuDeDonnees = [({'utilisateur': (1, 'John', 'Doe', 'johndoe', 'password123')})]
@pytest.mark.parametrize('client', jeuDeDonnees, indirect=True)
def test_auth_inexistant(client):
    """Teste l'authentification d'un utilisateur inexistant
    
    
    :param client: une instance de test
    :type client: FlaskClient
    """
    
    body = {
        "Username" : "joe",
        "Password" : "password123"
    }
    headers = {'Content-Type': 'application/json'}
    response = client.post('/utilisateurs/auth', json=body, headers=headers)
    
    assert response.status_code == 404
    
#type incorrect
jeuDeDonnees = [({'utilisateur': (1, 'John', 'Doe', 'johndoe', 'password123')})]
@pytest.mark.parametrize('client', jeuDeDonnees, indirect=True)
def test_auth_type_incorrect(client):
    """Teste l'authentification d'un utilisateur avec un type incorrect
    
    :param client: une instance de test
    :type client: FlaskClient
    """
    
    body = {
        "Username" : 123,
        "Password" : "password123"
    }
    headers = {'Content-Type': 'application/json'}
    response = client.post('/utilisateurs/auth', json=body, headers=headers)
    
    assert response.status_code == 400
    


