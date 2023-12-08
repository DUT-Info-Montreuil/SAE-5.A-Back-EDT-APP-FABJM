#!/usr/bin/env python
# coding: utf-8

# In[8]:


from conftest import client
import pytest
import os
import json





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
    response = client.get('/utilisateurs/getAll')
    print("utilisateurs = ", response.data)
    data = json.loads(response.data)
    #pytest.info(data)
    assert 'Gilgamesh' == data[1]['FirstName']





