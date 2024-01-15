from flask import jsonify
from src.apiException import ParamètreInvalideException

def query_update(tableName, where, data, necessaryKeys):
    """
    Crée une requête pour mettre à jour une table dans la base de données.

    :param: tableName: Le nom de la table à mettre à jour.
    :type tableName: str
    :param: where: La condition de la mise à jour.
    :type where: str
    :param: data : Un dictionnaire contenant les données à mettre à jour.
    :type data: dict
    :param: necessaryKeys : Une liste des clés nécessaires pour la mise à jour.
    :type necessaryKeys: liste

    :raise 400 Error: si une clé dans le dictionnaire de données est manquante ou invalide.

    :return: La requête générée.
    :rtype: str
    """
    tab_info = []

    for key in data.keys():
        if key not in necessaryKeys:
            error_message = f"Le paramètre {key} n'existe pas pour cette route"
            return jsonify({'error': ParamètreInvalideException(message="")}), 400
        tab_info.append(f"{key}='{data[key]}'")

    return f"UPDATE edt.{tableName} SET " + ", ".join(tab_info) + f" WHERE {where} RETURNING *"