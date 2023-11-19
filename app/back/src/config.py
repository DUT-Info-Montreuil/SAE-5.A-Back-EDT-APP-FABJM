#!/usr/bin/python
from configparser import ConfigParser

def config(filename='config.ini', section='postgresql'):
    """Récupere les paramètres de l'application dans le fichier de configuration

    :param filename: chemin vers le fichier de configuration, par défaut config.ini
    :type filename: String, optionnel
    
    :param section: nom de la section à rechercher, par défaut postgresql
    :type section: String, optionnel
    
    :raises Exception: Une section dans le fichier de configuration n'a pas été trouvé
    
    :return: les paramètre de la base donnée
    :rtype: dictionnaire
    """
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db