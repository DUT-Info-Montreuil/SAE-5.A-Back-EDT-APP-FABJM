# -*- coding: utf-8 -*-
# verification.py

def estDeTypeTime(string):
    """Détermine si un string respecte le format time (sql) hh:mm:ss

    :param string: Prends en paramètre d'entrée une chaine de string
    :type string: String
    
    :return: Retourne True si le string est un time, False sinon
    :rtype: bool
    """
    if len(string) != 8:
        return False
    try:
        for k in range(0,1):
            if not string[k].isdigit():
                return False

        if string[2] != ":":
            return False

        for k in range(3,4):
            if not string[k].isdigit():
                return False

        if string[5] != ":":
            return False

        for k in range(6,7):
            if not string[k].isdigit():
                return False

        return True
    
    except IndexError:
        return False

def estDeTypeTimeStamp(string):
    """Détermine si un string respecte le format TIMESTAMP (sql) yyyy-mm-jj

    :param string: Prends en paramètre d'entrée une chaine de string
    :type string: String
    
    :return: Retourne True si le string est un TimeStamp, False sinon
    :rtype: bool
    """
    if len(string) != 10:
        return False

    try :
        for k in range(0,3):
            if not string[k].isdigit():
                return False

        if string[4] != "/":
            return False

        for k in range(5,6):
            if not string[k].isdigit():
                return False

        if string[7] != "/":
            return False

        for k in range(8,9):
            if not string[k].isdigit():
                return False

        return True