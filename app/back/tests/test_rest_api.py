#!/usr/bin/env python
# coding: utf-8

# In[8]:


from conftest import client
import pytest
import os
import json

token = ""


def test_should_status_code_ok(client):
    response = client.get('/index')
    assert response.status_code == 200
    
def test_should_return_hello_world(client):
    response = client.get('/index')
    data = response.data.decode() 
    assert data == 'Hello, World!'

def test_chemin(client):
    path = os.path.dirname(os.path.dirname(os.getcwd())) + "/database"
    #print("try : ", client.get('/utilisateurs/auth').data)
    assert os.path.exists(path)


def test_empty_db(client):
    """Start with a blank database."""
    resp = client.get('/utilisateurs/getAll')
    data = json.loads(resp.data)
    #pytest.info(data)
    assert len(data) > 2

