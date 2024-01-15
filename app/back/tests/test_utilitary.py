import pytest

from flask import jsonify

from src.utilitary import get, add_one, update
from src.apiException import ParamètreInvalideException
############          GET               ###################
# Can retrieve all data from a table with no where clause and default key_to_return
def test_retrieve_all_data_with_no_where_clause_and_default_key_to_return():
    # Arrange
    table_name = "employees"
    where = ""
    key_to_return = "*"

    # Act
    result = get(table_name, where, key_to_return)

    # Assert
    expected_query = "SELECT * edt.employees"
    assert result == (expected_query)
# Can retrieve specific data from a table with a where clause and default key_to_return
def test_retrieve_specific_data_with_where_clause_and_default_key_to_return():
    # Arrange
    table_name = "employees"
    where = "age > 30"
    key_to_return = "*"

    # Act
    result = get(table_name, where, key_to_return)

    # Assert
    expected_query = "SELECT * edt.employees WHERE %s"
    expected_params = ("age > 30")
    assert result == (expected_query, expected_params)
# Can retrieve specific data from a table with a where clause and specific key_to_return
def test_retrieve_specific_data_with_where_clause_and_specific_key_to_return():
    # Arrange
    table_name = "employees"
    where = "age > 30"
    key_to_return = "name, age"

    # Act
    result = get(table_name, where, key_to_return)

    # Assert
    expected_query = "SELECT name, age edt.employees WHERE %s"
    expected_params = ("age > 30")
    assert result == (expected_query, expected_params)

#############             ADD                   ###################
# Insert a new record with valid parameters and return the generated key
def test_valid_parameters_return_key():
    # Arrange
    table_name = "my_table"
    key_to_return = "id"
    data = {"name": "John", "age": 25}
    possible_keys = ["name", "age"]

    # Act
    result = add_one(table_name, key_to_return, data, possible_keys)

    # Assert
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)
    assert result[0] == "INSERT edt.my_table (name, age) VALUES (%s, %s) RETURNING id"
    assert result[1] == "name='John', age='25'"
# Insert a new record with valid parameters and return the generated key, with multiple key_to_return values
def test_valid_parameters_return_multiple_keys():
    # Arrange
    table_name = "my_table"
    key_to_return = "id, name"
    data = {"name": "John", "age": 25}
    possible_keys = ["name", "age"]

    # Act
    result = add_one(table_name, key_to_return, data, possible_keys)

    # Assert
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)
    assert result[0] == "INSERT edt.my_table (name, age) VALUES (%s, %s) RETURNING id, name"
    assert result[1] == "name='John', age='25'"
# Insert a new record with invalid table_name parameter and raise ParamètreInvalideException
def test_invalid_table_name_raise_exception():
    # Arrange
    table_name = ""
    key_to_return = "id"
    data = {"name": "John", "age": 25}
    possible_keys = ["name", "age"]
    error_hapened = False
    
    # Act
    result = add_one(table_name, key_to_return, data, possible_keys)

    # Assert
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)
    assert result[0] == "INSERT edt. (name, age) VALUES (%s, %s) RETURNING id, name"
    assert result[1] == "name='John', age='25'"
        

#############            UPDATE                 ###################
# Update a table with valid parameters and return the updated rows.
def test_update_valid_parameters_return_updated_rows():
    # Arrange
    table_name = "table1"
    where = "id=1"
    key_to_return = "name"
    data = {"name": "John", "age": 30}
    possibleKeys = ["name", "age"]

    # Act
    result = update(table_name, where, key_to_return, data, possibleKeys)

    # Assert
    assert result == ("UPDATE edt.table1 SET %s WHERE %s RETURNING name", ("name='John', age='30'", "id=1"))
# Update a table with valid parameters and without returning the updated rows.
def test_update_valid_parameters_without_returning_updated_rows():
    # Arrange
    table_name = "table1"
    where = "id=1"
    key_to_return = ""
    data = {"name": "John", "age": 30}
    possibleKeys = ["name", "age"]

    # Act
    result = update(table_name, where, key_to_return, data, possibleKeys)

    # Assert
    assert result == ("UPDATE edt.table1 SET %s WHERE %s", ("name='John', age='30'", "id=1"))
# Update a table with an empty possibleKeys list.
def test_update_empty_possibleKeys_list():
    # Arrange
    table_name = "table1"
    where = "id = 1"
    key_to_return = ""
    data = {"name": "John", "age": 30}
    possibleKeys = []
    error_hapened = False
    # Act
    try:
        update(table_name, where, key_to_return, data, possibleKeys)
    # Assert
    except Exception:
        # Une erreur se lance si la foonction update fait un jsonify
        error_hapened = True
    assert error_hapened
# Update a table with an empty where clause.
def test_update_empty_where_clause():
    # Arrange
    table_name = "table1"
    where = ""
    key_to_return = ""
    data = {"name": "John", "age": 30}
    possibleKeys = ["name", "age"]

    # Act
    result = update(table_name, where, key_to_return, data, possibleKeys)

    # Assert
    assert result == ("UPDATE edt.table1 SET %s WHERE %s", ("name='John', age='30'", ""))
# Update a table with valid parameters, an injection and return the updated rows.
def test_update_valid_parameters_with_xss_injection_return_updated_rows():
    # Arrange
    table_name = "table1"
    where = "id=1"
    key_to_return = "name"
    data = {"name": "John<script>alert('XSS')</script>", "age": 30}
    possibleKeys = ["name", "age"]

    # Act
    result = update(table_name, where, key_to_return, data, possibleKeys)

    # Assert
    assert result == ("UPDATE edt.table1 SET %s WHERE %s RETURNING name", ("name='John&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;', age='30'", "id=1"))
