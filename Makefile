# Tâches

help:
	echo "pytest :  Installe la variable d'environment pytest"
	echo "setup : Installe le projet en tant que package"
	echo "install : Installe les dépendances"
	echo "test : Lance les tests"
	echo "clean  : Nettoie le projet"
	echo "sphinx  : Génère la documentation"

pytest:
	python -m pip install --user pytest
	python -m pip install --user flask

setup:
	pip install -e .

install:
	pipenv requirements > requirements.txt 

tests:
	python -m pytest tests/test_rest_api.py -v --html=tests/rapport.html

clean:
	rm -rf __pycache__ .pytest_cache
	
sphinx:
	sphinx-build -b html docs/documentDev/source/ docs/documentDev/build/
	
git:
	echo "a définir"
	
docker:
	echo "a définir

init: 
	pymake setup
	pymake sphinx
	
env:
	pipenv install
	pipenv shell python -m main  
	

