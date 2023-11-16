#!/usr/bin/env python
# coding: utf-8

# In[8]:


from conftest import client
import pytest

def test_should_status_code_ok(client):
    response = client.get('/index')
    assert response.status_code == 200
    
def test_should_return_hello_world(client):
    response = client.get('/index')
    data = response.data.decode() 
    assert data == 'Hello, World!'



