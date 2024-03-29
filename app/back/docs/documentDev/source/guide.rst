Guide de la partie back-end du projet Edt
=============================================

.. image:: images/edt.png
   :align: center
   :alt: Logo de l'edt
   :scale: 50%

Bienvenue dans la documentation du projet Edt. Ce document vous guidera à travers les différentes fonctionnalités et composants de notre projet. 
Les commandes suivantes sont à executer depuis le repertoire racine.

Installation
------------

Pour démarrer l'environnement virtuelle , exécutez la commande suivante :

.. code-block:: python

    pymake env

Pour installer le projet , exécutez la commande suivante :

.. code-block:: python

    pymake setup 
	
Pour quitter l'environnement virtuelle , exécutez la commande suivante :

.. code-block:: python

    exit


Utilisation
-----------

Après l'installation, vous pouvez lancer les tests et générer un rapport de la manière suivante :

.. code-block:: python

    pymake tests


.. note::

   Assurez-vous d'avoir toutes les dépendances requises installées (sinon exécutez la pymake env ) .
	
	
Pour mettre à jour vos dépendances :

.. code-block:: python
	
	pymake install
	
Pour installer un module :

.. code-block:: python
	
	pipenv install {nom-module}

.. note::

   Penser à mettre jour les dépendances avec pymake install après avoir installer un nouveau module
	
Documentation
--------------

Pour regénérer la documentation :

.. code-block:: python
	
	pymake sphinx
	
Pour modifier cette page  :

.. code-block:: 
	
	modifier le fichier guide.rst présent dans le dossier ./docs/documentDev/source/
	
Pour créer une nouvelle page  :

.. code-block:: 
	
	créer un fichier.rst dans le dossier ./docs/documentDev/source/ puis ajouter le dans "l'arbre" du fichier index.rst présent dans le même répertoire.
	
Pour documenter vos fonctions, vous devrez écrire des docstrings suivant la syntaxe ci-dessous (voir dans références) :

.. code-block:: python
	
	"""Résumé de la fonction

	:param [nomParamètre]: [descriptionParamètre], par défaut [valeurParDefaut]
	:type [nomParamètre]: [typeParamètre](, optionnel)
	
	:raises [TypeException]: [DescriptionErreur]
	
	:return: [DescriptionReturn]
	:rtype: [TypeReturn]

	"""

	
Si vous voulez modifier la page API Reference (générer automatiquement) :

.. code-block:: 
	
	vous devrez modifier directement les docstrings
	

	
	
Fichier rst
-----------

Pour créer un fichier rst, celui-ci  commence toujours par un titre définit comme ci-dessous  :

.. code-block:: RST
	
	titre
	=====
	
Pour définir un chapitre :

.. code-block:: RST
	
	chapitre
	--------
	
.. note::

   A noter les deux marqueurs vu précédement doivent être aussi long que le mot sur lequel il s'applique
   
Pour définir une note :

.. code-block:: RST

	.. note::
	
		message
	
Pour insérer une image :

.. code-block:: RST

	.. image:: cheminImage
	   :align: alignementImage
	   :alt: descriptionImage
	   :scale: tailleImage


Structure du projet
-------------------

Ce projet est composés de différents fichiers et répertoires.

- Un répertoire src/ contenant le code de l'application
- Un répertoire tests/ contenant les tests de l'application
- Un répertoire docs/ contenant la documentation de l'application
- Un ficher .gitignore pour que git ignore certaines extensions de fichiers 
- Un fichier LICENSE contenant la license de notre projet afin de nous couvrir juridiquement
- Un fichier Makefile pour définir des commandes personnalisé, notamment pour de l'automatisation de Git et Docker
- Un fichier MANIFEST.in permettant d'inclure des fichiers ou des répertoires qui ne sont pas automatiquement inclus par les outils de construction de paquets.
- Un fichier README.md servant de documentation d'introduction pour le projet
- Un fichier requirements.txt contenant toutes les dépendances externes dont à besoin notre projet pour fonctionner
- Un fichier Pipfile qui stocke les dépendances d'un projet Python géré par Pipenv
- Un fichier Pipfile.lock qui verrouille les versions exactes des dépendances d'un projet Python géré par Pipenv
- Et un fichier setup.py qui s'occupe de la gestion de la distribution et de la création des paquets

Contributeurs
-------------
- Fabrice AMEGADJEN

.. versionadded:: 0.1.0
	Initialisation du projet 


Références
----------

- `Documentation Sphinx <https://www.sphinx-doc.org/en/master/>`_
- `reStructuredText Directives <https://docutils.sourceforge.io/docs/ref/rst/directives.html>`_
- `Structure projet Flask <https://python-guide-pt-br.readthedocs.io/fr/latest/writing/structure.html>`_
- `Structure docstring Sphinx <https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html>`_
