# -*- coding: utf-8 -*-
"""uploader.py
Uploading functions.

This module handles pre-processing of uploaded data and passes it to
the database functions in the dblib.py module.


@author: Eric
"""
import string
from flask import request
import dblib


def upload_file():
    """Process an uploaded CSV file.
    This only processes the first file uploaded.
    Read in the file.
    Create a database table with the same name as the file name.
    The columns of the table are the columns of the CSV file.
    Reads the data and inserts the data into the table.

    Args:
        None

    Returns:
        None if the upload was successful.
        Error message if the upload failed.
    """
    file_obj = get_file_obj()
    if not file_obj:
        return 'Please upload a CSV file'

    # Get the filename.
    filename = file_obj.filename
    if filename.endswith('.csv'):
        cleaned_filename = filename[:-4]
    else:
        cleaned_filename = filename
    table_name = clean_word(cleaned_filename)

    # Get the contents.
    file_contents = file_obj.read()
    file_obj.close()
    if not file_contents:
        return 'The file was empty'

    # Insert information about the new table into the index.
    table_setup_error = dblib.insert_table_index(table_name, filename)
    if table_setup_error:
        if table_setup_error is dblib.ID_EXISTS_MESSAGE:
            # Try to update this table.
            # But, this could be changed to disallow updates.
            print 'Table entry exists, but trying to update'
            pass
        else:
            return table_setup_error

    # Process the contents.
    contents_list = file_contents.splitlines()

    # Get the column names.
    col_names = contents_list[0].split(',')
    col_names = [clean_word(col_name) for col_name in col_names]
    if None in col_names:
        return 'Invalid column name'

    # Create the table.
    creation_error = dblib.create_db_table(table_name, col_names)
    if creation_error:
        if creation_error is dblib.TABLE_EXISTS_MESSAGE:
            # Try to update this table.
            # But, this could be changed to disallow updates.
            print 'Table exists, but trying to update.'
            pass
        else:
            return creation_error

    insert_error_count = 0
    for row in contents_list[1:]:
        row = row.strip()
        if not row:
            continue
        row_data = row.split(',')
        nonnull_columns, nonnull_data = match_columns_data(col_names,
                                                           row_data)
        if not nonnull_columns:
            continue
        # Could add a check here for whether or not the insert was successful.
        # And if it seemed like the row already existed,
        # it could try an UPDATE instead of an INSERT.
        insert_error = dblib.insert_row(table_name,
                                        nonnull_columns,
                                        nonnull_data)
        if insert_error:
            insert_error_count += 1
    if insert_error_count >= len(contents_list[1:]):
        return 'Data could not be saved.'
    elif insert_error_count > 0:
        return 'Partial success: Not all rows were successfully saved.'
    else:
        return None


def match_columns_data(column_names, row_data):
    """Match up nonnull cells with their columns.
    Iterate through the row of data and skip any columns that have no data.

    Args:
        column_names: The names of all the columns. A list.
        row_data: The row of data. A list.

    Returns:
        nonnull_columns: A list of the nonnull column names.
        nonnull_row: A list of the nonnull row data.
    """
    nonnull_columns = []
    nonnull_data = []
    for column, data in zip(column_names, row_data):
        if data:
            nonnull_columns.append(column)
            nonnull_data.append(data)
    return nonnull_columns, nonnull_data


def get_file_obj():
    """Get the uploaded file's Flask FileStorage object.

    Args:
        None

    Returns:
        Flask FileStorage object of the first uploaded file.
    """
    if not request.files:
        return None
    # Grab the first file.
    first_file = request.files.keys()[0]
    uploaded_file = request.files[first_file]
    if not uploaded_file:
        return None
    else:
        return uploaded_file


def clean_word(word):
    """Ensure that this word is a valid SQL table or column name.
    Make sure first character is alphabetical or _.
    Remove punctuation (except underscores) and whitespaces.

    Args:
        word: The word to be cleaned.

    Returns:
        cleaned_word: The cleaned word.
    """
    cleaned_word = word.decode('utf-8', 'ignore')
    # Make the word ASCII
    cleaned_word = cleaned_word.encode('ascii', 'ignore')
    cleaned_word = str(cleaned_word)
    cleaned_word = cleaned_word.strip()
    if not cleaned_word:
        return None
    if not cleaned_word[0].isalpha() and cleaned_word[0] != '_':
        cleaned_word = '_' + cleaned_word
    # Remove whitespaces.
    cleaned_word = cleaned_word.translate(None, string.whitespace)
    # Remove punctuation except for underscore.
    punc_no_under = string.punctuation.replace('_', '')
    cleaned_word = cleaned_word.translate(None, punc_no_under)
    return cleaned_word
