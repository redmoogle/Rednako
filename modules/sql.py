"""
handles SQL
"""
import os
import sqlite3
import logging

def add(table, values):
    """
    Writes to a sql table with provided values

        Parameters:
            table (str): table to add to
            values (tuple): values to add

        Returns:
            Success (bool): Did it succede
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
    except sqlite3.OperationalError as error:
        logging.error('SQL-ADD Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def update(table, source, change, where: list = None):
    """
    Update a sql table with provided values and location

        Parameters:
            table (str): table to update
            source (str): What datapoint to modify
            change (str): What to change the datapoints too
            where (list): Filter what your changing

        Returns:
            Success (bool): Did it succede
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _sqlstring = ''
    if where:
        for index, args in enumerate(where):
            if index == 1:
                _sqlstring += ' WHERE '
            if index%2 == 0:
                _sqlstring += f'= {args} '
            else:
                _sqlstring += f'{args} '
            if(index != len(where)) and (index%2 == 0):
                _sqlstring += 'AND '

    # Check if it executed
    try:
        pointer.execute(f'UPDATE {table} SET {source} = {change}{_sqlstring}')
        logging.info('SQL-UPDATE: "UPDATE %s SET %s = %s%s"', table, source, change, _sqlstring)
    except sqlite3.OperationalError as error:
        logging.error('SQL-UPDATE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def remove(table, where: list = None):
    """
    Removes data from a table provided values

        Parameters:
            table (str): table to remove from
            where (list): Filter on what to remove

        Returns:
            Success (bool): Did it succede
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _sqlstring = ''
    if where:
        for index, args in enumerate(where):
            if index == 1:
                _sqlstring += ' WHERE '
            if index%2 == 0:
                _sqlstring += f'= {args} '
            else:
                _sqlstring += f'{args} '
            if(index != len(where)) and (index%2 == 0):
                _sqlstring += 'AND '

    # Check if it executed
    try:
        pointer.execute(f'DELETE FROM {table} {_sqlstring}')
        logging.info('SQL-DELETE: "DELETE FROM %s %s"', table, _sqlstring)
    except sqlite3.OperationalError as error:
        logging.error('SQL-REMOVE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def create_table(table: str, types: list, check_exist: bool = False):
    """
    Creates a SQL table with provided values

        Parameters:
            table (str): table to create
            types (list): columns to add
            check_exist (bool): Check if it already exists

        Returns:
            Success (bool): Did it succede
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()
    # Check if it executed

    # construct (X: TYPE, B: TYPE)
    _sqlstring = ''
    for index, _type in enumerate(types):
        if index%2 == 1: # spacing
            _sqlstring += ' '
        _sqlstring += f'{_type}'
        if(index != len(types)) and (index%2 == 0): # dont append a comma onto the end
            _sqlstring += ', '

    if check_exist:
        exist = 'IF NOT EXISTS'
    else:
        exist = ''

    try:
        pointer.execute(f'CREATE TABLE {exist} {table} ({_sqlstring})')
        logging.info('SQL-CREATE: "CREATE TABLE %s %s (%s)"', exist, table, _sqlstring)
    except sqlite3.OperationalError as error:
        logging.error('SQL-CREATE Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def remove_table(table, check_exist: bool = False):
    """
    Drop a SQL table

        Parameters:
            table (str): table to drop
            check_exist (bool): Check if it exists

        Returns:
            Success (bool): Did it succede
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
    except sqlite3.OperationalError as error:
        logging.error('SQL-DROP Error: %s', error)
        return False
    database.commit()
    database.close()
    return True

def select(table, where: list = None, toselect: str = '*'):
    """
    Grab data from a given sql table

        Parameters:
            table (str): table to grab from
            where (list): Filter what your grabbing
            toselect (str): What column to grab

        Returns:
            data (list): data fetched from table
    """
    datapath = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data"))
    sqldb = f"{os.path.join(datapath, 'database.db')}"
    # Pointer to the database
    database = sqlite3.connect(sqldb)
    # Cursor of the database
    pointer = database.cursor()

    # construct WHERE x AND...
    _sqlstring = ''
    if where:
        for index, args in enumerate(where):
            if index == 1:
                _sqlstring += ' WHERE '
            if index%2 == 0:
                _sqlstring += f'= {args} '
            else:
                _sqlstring += f'{args} '
            if(index != len(where)) and (index%2 == 0):
                _sqlstring += 'AND '

    # Check if it executed
    try:
        _params = pointer.execute(f'SELECT {toselect} FROM {table}{_sqlstring}')
        logging.info('SQL-SELECT: "SELECT %s FROM %s%s"', toselect, table, _sqlstring)
    except sqlite3.OperationalError as error:
        logging.error('SQL-SELECT Error: %s', error)
        return False

    fetchpass = _params.fetchall() # have to do this before the connection is yeeted
    database.commit()
    database.close()
    return fetchpass

def raw_sql(sql):
    """
    Grab data from a given sql table

        Parameters:
            sql (str): SQL to execute

        Returns:
            data (list): data from that sql
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
    except sqlite3.OperationalError as error:
        logging.error('SQL-RAW Error: %s', error)
        return False
    fetchpass = output.fetchall() # cant fetch on a closed DB
    database.commit()
    database.close()
    return fetchpass
