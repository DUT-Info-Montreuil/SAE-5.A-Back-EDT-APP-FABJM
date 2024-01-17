import hashlib
from flask import jsonify
from markupsafe import escape
from src.apiException import ParamètreInvalideException

def get(table_name, where=None, key_to_return=["*"]):
    """
    Récupérer les données d'une table spécifiée dans la base de données.

    :param table_name: Le nom de la table à partir de laquelle récupérer les données.
    :type table_name: str
    :param where: La condition pour filtrer les données.
    :type where: str
    :param key_to_return: La ou les clés à renvoyer de la table. La valeur par défaut est "*".
    :type key_to_return: str, optional

    :return: Un tuple contenant la requête SQL et les paramètres de la requête si il y en a.
    :rtype: tuple
    """
    get_query =  "SELECT " + ", ".join(key_to_return) + " FROM edt." + table_name
    if where != None:
        tab_condition = []
        for filtre in where.keys():
            tab_condition.append(filtre+"=%s")
        get_query += " WHERE "+" AND ".join(tab_condition)
        return (get_query, tuple([where[key.split("=")[0]] for key in tab_condition]))
    return (get_query)

def add_one(table_name, key_to_return, data, possible_keys):
    """
    Insère un nouvel enregistrement dans une table spécifiée et renvoie la valeur clé générée.

    :param table_name: Le nom de la table dans laquelle insérer l'enregistrement.
    :type table_name: str
    :param key_to_return: Les noms des colonnes clés à renvoyer après l'insertion.
    :type key_to_return: str
    :param data: Les données à insérer dans la table.
    :type data: dict
    :param possible_keys: La liste des clés possibles pour les données.
    :type possible_keys: list

    :raises ParamètreInvalideException: Si un paramètre est invalide.
    
    :return: Un tuple contenant la requête d'insertion et les valeurs à insérer.
    :rtype: tuple
    """
    insert_query =  "INSERT edt." + table_name
    tab_keys = []
    tab_values = []
    for key in data.keys():
        # Est-ce que key est une clé possible
        if key not in possible_keys:
            error_message = f"Le paramètre {key} n'existe pas pour cette route"
            return jsonify({'error': ParamètreInvalideException(key)}), 400
            # return jsonify({'error': ParamètreInvalideException(message=error_message)}), 400
        # Echaper au balise qui aurait pu être mit en input par l'utilisateur
        data[key] = escape(data[key])
        tab_keys.append(key)
        tab_values.append(f"{key}='{data[key]}'")

    insert_query += f" ({', '.join(tab_keys)}) VALUES ({', '.join(['%s' for k in tab_keys])})"
    value_to_add = ", ".join(tab_values)
    if key_to_return:
        insert_query += " RETURNING " + key_to_return
    # Create string of set value
    return (insert_query, (value_to_add))

def update(table_name, where, key_to_return, data, possible_keys):
    """
    Crée une requête pour mettre à jour une table dans la base de données.

    :param table_name: Le nom de la table à mettre à jour.
    :type table_name: str
    :param where: La condition de la mise à jour.
    :type where: str
    :param key_to_return: La clé à retourner dans la requête UPDATE. Si elle est spécifiée, la requête retournera la valeur de cette clé pour chaque ligne mise à jour.
    :type key_to_return: str
    :param data : Un dictionnaire contenant les données à mettre à jour.
    :type data: dict
    :param possible_keys : Une liste des clés possibles pour la mise à jour.
    :type possible_keys: liste

    :raise 400 Error: si une clé dans le dictionnaire de données est invalide.

    :return: Les arguments pour une update et sont query.
    :rtype: tuple
    """
    update_query =  "UPDATE edt." + table_name + " SET %s WHERE "+" AND ".join([filtre+"=%s" for filtre in where.keys()])
    if key_to_return:
        update_query += " RETURNING " + key_to_return
    tab_query = []
    for key in data.keys():
        # Est-ce que key est une clé possible
        if key not in possible_keys:
            error_message = f"Le paramètre {key} n'existe pas pour cette route"
            return jsonify({'error': ParamètreInvalideException(key)}), 400
            # return jsonify({'error': ParamètreInvalideException(message=error_message)}), 400
        # Echaper au balise qui aurait pu être mit en input par l'utilisateur
        data[key] = escape(data[key])
        tab_query.append(f"{key}='{data[key]}'")
    # Create string of set value
    value_to_set = ", ".join(tab_query)
    return (update_query, (value_to_set, *tuple(value for value in where)))

def delete(table_name, where, key_to_return):
    """
    Deletes rows from a specified table based on a given condition.

    Args:
        table_name (str): The name of the table from which rows will be deleted.
        where (str): The condition used to determine which rows to delete.
        key_to_return (str): Optional. The key to return after deleting the rows.

    Returns:
        tuple: A tuple containing the delete query and the parameters for the query.

    """
    delete_query =  "DELETE edt." + table_name + " WHERE "+" AND ".join([filtre+"=%s" for filtre in where.keys()])
    if key_to_return:
        delete_query += " RETURNING " + key_to_return
    return (delete_query, tuple(value for value in where))

def password_encode(password):
    salt = "4di"
    salt_password = password+salt
    encode_password = hashlib.md5(salt_password.encode())
    return encode_password.hexdigest()

def where_builder(where):
    text = " WHERE "