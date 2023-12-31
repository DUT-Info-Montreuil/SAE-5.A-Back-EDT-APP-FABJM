import os
print(os.getcwd())
path = os.path.dirname(os.path.dirname(os.getcwd())) + r"\database"
print(path)
        if app.config['TESTING']:
        # Utilisez la base de données virtuelle pour les tests
        app.config['DATABASE'] = sqlite3.connect(':memory:')
    else:
        # Utilisez la base de données spécifiée dans la configuration
        app.config['DATABASE'] = sqlite3.connect(app.config['DATABASE_URI'])
#python test/chemin.py

python -m pytest tests/test_rest_api.py -v --html=tests/rapport.html

[{"FirstLogin": true,"FirstName": "Junko","IdUtilisateur": 1,"LastName": "Enoshima","PassWord": "despair","Username": "monokuma"
 },
  {
    "FirstLogin": true,
    "FirstName": "Gilgamesh",
    "IdUtilisateur": 2,
    "LastName": "Elish",
    "PassWord": "Enkidu",
    "Username": "Uruk"
  },
  {
    "FirstLogin": true,
    "FirstName": "Aya",
    "IdUtilisateur": 3,
    "LastName": "Rindo",
    "PassWord": "immortal",
    "Username": "detective"
  },
  {
    "FirstLogin": true,
    "FirstName": "Tsugaru ",
    "IdUtilisateur": 4,
    "LastName": "Shinuchi",
    "PassWord": "OniKiller",
    "Username": "assistant"
  }
]