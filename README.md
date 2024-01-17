# SAe-5.A-Temp-EDT-APP
Armand
Bastien
Fabrice
Jérémy
Maxime

Bienvenue dans le guide pour installer la partie back-end du projet Edt visant à mettre en place un emploie du temps.

Sur Docker : 
    - Commencer par lancer la commande cd app/back
	- Puis lancer la commande make compose 
    - Ensuite ouvrez un autre terminal puis cherchez id du container de la db en cours à l'aide de la commande docker ps

    Puis ouvrez le terminal de ce container que vous venez de trouver:
    docker exec -it container_id bash

    Enfin exécutez ces commandes dans les terminaux respectifs : 

    Dans le terminal de la BDD :
        su postgres -
        cd
        cd commands/SQL_script
        psql
        \i commands.sql

    Dans le terminal du back (ici on ne prend pas en compte les tests) : 
        python -m pip install --upgrade pip
        pip install pipenv --upgrade
        apt-get update
        apt-get -y install libpq-dev gcc
        pip install py-make
        pip install -r requirements.txt
        pip install flask_jwt_extended
        cd ..
        pip install -e .
        cd /usr
        python app/back/src/rest_api.py

Pour Windows : 
    Pour utiliser et obtenir plus d'information sur ce projet :
        -   Soit déplacer vous d'abord dans app/back avec *cd app/back*, puis executer la commmande *pip install py-make==0.1.1*, ensuite lancer *pip env* suivi de la commande *pymake initW* puis rendez-vous au fichier docs/documentDev/build/index.html afin de consulter la documentation.
        -   Ou executer le script mmm à la racine.

Pour Linux :
    Pour utiliser et obtenir plus d'information sur ce projet :
        -   Déplacer vous d'abord dans app/back avec *cd app/back*, puis executer la commmande *make setup*, puis *make pytest* puis rendez-vous au fichier docs/documentDev/build/index.html afin de consulter la documentation.
