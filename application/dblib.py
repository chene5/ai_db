# -*- coding: utf-8 -*-
"""dblib.py
Database interaction functions.

This is the only module that interacts with the database.
These functions provide information about the database,
create tables, and insert new data into tables.


@author: Eric
"""
import sqlalchemy
from config import SQLALCHEMY_DATABASE_URI
from models import TableIndex
from application import db

# These are utility tables in the DB and shouldn't be displayed.
TABLE_EXCLUDES = ['migrate_version', 'tableIndex']

# These are error messages.
TABLE_EXISTS_MESSAGE = 'This dataset already exists'
ID_EXISTS_MESSAGE = 'UNIQUE constraint failed'
DUPLICATE_COLUMN_MESSAGE = 'Duplicate column name error'
DUPLICATE_COLUMN_ERROR = 'duplicate column name'


def create_db_table(table_name, col_names):
    """Create a table in the database.
    Create a SQL CREATE TABLE command string, then execute the command.
    All columns are created as VARCHAR columns.

    Args:
        table_name: The name of the table. A string.
        col_names: A list of the names of the columns.

    Returns:
        None if operation was successful.
        Error message if execution raised an error.
    """
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    create_command = 'CREATE TABLE "{}" ('.format(table_name)
    for col in col_names:
        # Create all columns as VARCHAR
        create_command += '{} VARCHAR, '.format(col)
    # Set the first column to be the primary key.
    create_command += 'PRIMARY KEY ({}));'.format(col_names[0])
    stmt = sqlalchemy.text(create_command)
    try:
        engine.execute(stmt)
    except sqlalchemy.exc.OperationalError as e:
        print e
        if 'already exists' in str(e):
            print "already exists"
            return TABLE_EXISTS_MESSAGE
        elif DUPLICATE_COLUMN_ERROR in str(e):
            print DUPLICATE_COLUMN_MESSAGE
            return DUPLICATE_COLUMN_MESSAGE
        else:
            return 'Operational Error occurred'
    except ValueError as e:
        print e
        return 'Invalid identifier used'
    except:
        # return 'SQL Engine Error occurred'
        raise
    return None


def insert_table_index(table_name, filename):
    """INSERT a table information into the table index.
    This uses SQLAlchemy's ORM model functionality.

    Args:
        table_name: The name of the table to INSERT into.
        filename: The original filename of the CSV file.

    Returns:
        None if operation was successful.
        Error message if execution raised an error.
    """
    table_index = TableIndex(table_name=table_name,
                             filename=filename)
    db.session.add(table_index)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print e
        if ID_EXISTS_MESSAGE in str(e):
            print ID_EXISTS_MESSAGE
            return ID_EXISTS_MESSAGE
        else:
            return 'Operational Error occurred'
    except:
        # return 'SQL Engine Error occurred'
        raise
    return None


def insert_row(table_name, columns, row_data):
    """INSERT a row of data into a table.

    Args:
        table_name: The name of the table to INSERT into.
        columns: The columns for the data. A list.
        row_data: The data for the row that will be inserted. A list.

    Returns:
        None if operation was successful.
        Error message if execution raised an error.
    """
    if not verify_table_name(table_name):
        return 'Table is not in the database'
    if not row_data:
        return 'No data to insert'
    insert_command = create_insert_command(table_name, columns, row_data)
    if not insert_command:
        return 'INSERT command construction error'
    param_dict = create_param_dict(row_data)
    stmt = sqlalchemy.text(insert_command)
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    try:
        engine.execute(stmt, param_dict)
    except sqlalchemy.exc.IntegrityError as e:
        print e
        if ID_EXISTS_MESSAGE in str(e):
            print ID_EXISTS_MESSAGE
            return ID_EXISTS_MESSAGE
        else:
            return 'Integrity Error occurred'
    except:
        # return 'SQL Engine Error occurred'
        raise
    return None


def create_insert_command(table_name, columns, row_data):
    """Create a INSERT command that will use bound parameters.
    The checks for the table name and column names protect against
    SQL injections. It uses parameter names so that the execute()
    command can escape and add the parameters.

    Args:
        table_name: The name of the table to INSERT into.
        columns: The columns with new data.
        row_data: The row of data to INSERT.

    Returns:
        insert_command: The SQL INSERT command with named parameters.
            Looks like this:
                INSERT INTO table_name (column1, column2, ...columnN) VALUES
                    (:col1, :col2, ...colN)
        None if the table name or one of the column names is invalid.
    """
    if not verify_table_name(table_name):
        print 'Table is not in the database'
        return None
    if not verify_column_names(table_name, columns):
        print 'Not all columns are in the table'
        return None
    insert_command = 'INSERT INTO "{}" ('.format(table_name)
    insert_command += '{}'.format(','.join(columns))
    insert_command += ') VALUES ('
    for i in range(0, len(row_data)):
        insert_command += ':col{},'.format(i)
    insert_command = insert_command.rstrip(',')
    insert_command += ')'
    return insert_command


def create_param_dict(row_data):
    """Create parameter dictionary for use with bound parameters.
    This sets up the SQLAlchemy engine to escape the parameters and
    avoid SQL injection attacks.

    Args:
        row_data: The row of data to be added.

    Returns:
        param_dict: A dictionary of the parameters and data. The
            keys for the dictionary are col[i]. It looks like this:
            {col1: data1,
             col2: data2,
             ...
             colN: dataN}
    """
    param_dict = {}
    for i in range(0, len(row_data)):
        param_name = 'col{}'.format(i)
        param_dict[param_name] = row_data[i]
    return param_dict


def get_table_names():
    """Get the names of the tables in the db.
    Inspect the db for the names of the tables.

    Args:
        None

    Returns:
        A list of the table names.
    """
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    inspector = sqlalchemy.inspect(engine)
    # Get table names
    table_names = inspector.get_table_names()
    return table_names


def verify_table_name(table_name):
    """Check if table_name is actually a table in the database.
    This also might help prevent a SQL injection attack
    when we're building the SQL command.

    Args:
        table_name: The name of the table to test.

    Returns:
        True if the named table is in the database.
        False if the named table is not in the database.
    """
    table_names = get_table_names()
    if table_name in table_names:
        return True
    else:
        return False


def verify_column_names(table_name, test_columns):
    """Check if named columns are actually in the table.
    This also might help prevent a SQL injection attack
    when we're building the SQL command.

    Args:
        table_name: The name of the table to test.
        columns: The names of the columns to test.

    Returns:
        True if all the named columns are in the table.
        False if the named columns are in the table.
    """
    column_names = get_column_names(table_name)
    for column in test_columns:
        if column not in column_names:
            return False
    return True


def get_column_information(table_name):
    """Get the column information for a table by inspecting the db.

    Args:
        table_name: The name of the table in the db.

    Returns:
        A list of the column attributes, which includes the name.
    """
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    inspector = sqlalchemy.inspect(engine)
    # Get table names
    column_information = inspector.get_columns(table_name)
    return column_information


def get_column_names(table_name):
    """Get the column names for a table.
    Call get_column_information() to get the column information for the table.
    Iterate through the information list to build a list of the names.

    Args:
        table_name: The name of the table in the db.

    Returns:
        A list of the column names.
    """
    column_information = get_column_information(table_name)
    column_names = []
    for column in column_information:
        column_names.append(column['name'])
    return column_names


def get_data(table_name):
    """Get all data from the specified table."""
    if not verify_table_name(table_name):
        return None
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()
    stmt = sqlalchemy.text("SELECT * FROM {}".format(table_name))
    result = conn.execute(stmt)
    return result


def get_filename(table_name):
    """Get the original filename of the given table."""
    table_data = TableIndex.query.filter_by(table_name=table_name).first()
    return table_data.filename


def get_all_table_info():
    """Get the table names and original filenames for
    all the tables in the database.

    Args:
        None

    Returns:
        table_info: A list of all pairs of table names and filenames.
    """
    table_info = []
    tables = TableIndex.query.all()
    for table in tables:
        table_info.append([table.table_name, table.filename])
    return table_info
