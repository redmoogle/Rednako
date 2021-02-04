"""
handles SQL
"""
import os
import sqlite3
import logging

def add(table, values):
    """
    Insert something into the database
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()
    # Check if it executed
    try:
        pointer.execute(f'INSERT INTO {table} VALUES {values}')
        logging.info('SQL-ADD: "INSERT INTO %s VALUES %s"', table, values)
    except Exception as error:
        logging.error('SQL-ADD Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def update(table, what, moveto, where: list = None):
    """
    Update something in the database
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _itercalc = 0
    _sqlstring = ''
    if where:
        for this in where:
            _itercalc += 1
            if _itercalc == 1:
                _sqlstring += ' WHERE '
            if _itercalc%2 == 0:
                _sqlstring += f'= {this} '
            else:
                _sqlstring += f'{this} '
            if(_itercalc != len(where)) and (_itercalc%2 == 0):
                _sqlstring += 'AND '

    # Check if it executed
    try:
        pointer.execute(f'UPDATE {table} SET {what} = {moveto}{_sqlstring}')
        logging.info('SQL-UPDATE: "UPDATE %s SET %s = %s%s"', table, what, moveto, _sqlstring)
    except Exception as error:
        logging.error('SQL-UPDATE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def remove(table, where: list = None):
    """
    Remove something in the database
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _itercalc = 0
    _sqlstring = ''
    for this in where:
        _itercalc += 1
        if _itercalc == 1:
            _sqlstring += 'WHERE '
        if _itercalc%2 == 0:
            _sqlstring += f'= {this} '
        else:
            _sqlstring += f'{this} '
        if(_itercalc != len(where)) and (_itercalc%2 == 0):
            _sqlstring += 'AND '

    # Check if it executed
    try:
        pointer.execute(f'DELETE FROM {table} {_sqlstring}')
        logging.info('SQL-DELETE: "DELETE FROM %s %s"', table, _sqlstring)
    except Exception as error:
        logging.error('SQL-REMOVE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def create_table(table: str, types: list, check_exist: bool = False):
    """
    Create a table
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()
    # Check if it executed

    # construct (X: TYPE, B: TYPE)
    _itercalc = 0
    _sqlstring = ''
    for _type in types:
        _itercalc += 1
        if _itercalc%2 == 1: # spacing
            _sqlstring += f'{_type} '
        else:
            _sqlstring += f'{_type}'
        if(_itercalc != len(types)) and (_itercalc%2 == 0): # dont append a comma onto the end
            _sqlstring += ', '

    if check_exist:
        exist = 'IF NOT EXISTS'
    else:
        exist = ''

    try:
        pointer.execute(f'CREATE TABLE {exist} {table} ({_sqlstring})')
        logging.info('SQL-CREATE: "CREATE TABLE %s %s (%s)"', exist, table, _sqlstring)
    except Exception as error:
        logging.error('SQL-CREATE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def remove_table(table, check_exist: bool = False):
    """
    drop a table
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    if check_exist:
        exist = 'IF EXISTS'
    else:
        exist = ''

    # Check if it executed
    try:
        pointer.execute(f'DROP TABLE {exist} {table}')
        logging.warning('SQL-DROP: "DROP TABLE %s %s"', exist, table)
    except Exception as error:
        logging.error('SQL-DROP Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def select(table, where: list = None, toselect: str = '*'):
    """
    Insert something into the database
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _itercalc = 0
    _sqlstring = ''
    if where:
        for this in where:
            _itercalc += 1
            if _itercalc == 1:
                _sqlstring += ' WHERE '
            if _itercalc%2 == 0:
                _sqlstring += f'= {this} '
            else:
                _sqlstring += f'{this} '
            if(_itercalc != len(where)) and (_itercalc%2 == 0):
                _sqlstring += 'AND '

    # Check if it executed
    try:
        _params = pointer.execute(f'SELECT {toselect} FROM {table}{_sqlstring}')
        logging.info('SQL-SELECT: "SELECT %s FROM %s%s"', toselect, table, _sqlstring)
    except Exception as error:
        logging.error('SQL-SELECT Error: %s', error)
        return False

    fetchpass = _params.fetchall() # have to do this before the connection is yeeted
    database.commit()
    database.close()
    return fetchpass

def raw_sql(sql):
    """
    Execute raw SQL
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()
    # Check if it executed
    try:
        logging.warning('SQL-RAW: "%s"', sql)
        output = pointer.execute(sql)
    except Exception as error:
        logging.error('SQL-RAW Error: %s', error)
        return False
    fetchpass = output.fetchall() # cant fetch on a closed DB
    database.commit()
    database.close()
    return fetchpass
