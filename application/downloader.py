# -*- coding: utf-8 -*-
"""downloader.py
Functions to download datasets.

These functions handle and validate dataset download requests,
and format them into CSV files for downloading.


@author: Eric
"""
import StringIO
import csv
from flask import make_response
import dblib


def download_dataset(dataset_name):
    """Download a dataset from the db.

    Args:
        dataset_name: The name of the dataset, which is the name of a table.

    Returns:
        response: A Flask formatted response of type CSV.
        None if the download request failed.
    """
    if dataset_name in dblib.TABLE_EXCLUDES:
        # This was an attempt to read a protected table.
        return None
    # Retrieve the column names first.
    # Note that doing this gives us an extra layer of protection against
    # a SQL injection attack (e.g., if dataset_name is maliciously formed).
    # This will fail if dataset_name is not the name of a database.
    column_names = dblib.get_column_names(dataset_name)
    if not column_names:
        return None

    # Get the data from the database.
    data = dblib.get_data(dataset_name)

    # Use a StringIO object because it has a write() method.
    csv_stringio = StringIO.StringIO()
    # csv.writer will convert the list to a comma-separated string.
    # Write to the StringIO object.
    csv_writer = csv.writer(csv_stringio)
    csv_writer.writerow(column_names)
    csv_writer.writerows(data)
    # Get the data as a string.
    csv_contents = csv_stringio.getvalue()
    csv_stringio.close()

    # Get the original filename from the tableIndex table.
    filename = dblib.get_filename(dataset_name)
    # Make a Flask CSV type response.
    response = gen_csv_response(csv_contents, filename)
    return response


def gen_csv_response(csv_str, filename):
    """Format the CSV string into a Flask response with the right headers."""
    response = make_response(csv_str)
    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'
    return response
