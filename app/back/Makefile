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

test:
	python3 -m pytest tests/test_rest_api.py -v --html=tests/rapport.html

clean:
	rm -rf __pycache__ .pytest_cache
	
sphinx:
	sphinx-build -b html docs/documentDev/source/ docs/documentDev/build/
	
git:
	echo "a définir"
	
docker:
	docker build . -t projet_edt
	docker run -it --entrypoint /bin/bash --name projet_edt_instance projet_edt

compose:
	docker compose run --rm --entrypoint /bin/bash  --service-ports app

initW:
	pymake env
	pymake setup
	pymake sphinx

initL:
	make setup
	make sphinx
	
env:
	pipenv install --dev
	pipenv shell python -m main  
	
run:
	cd src && python rest_api.py
