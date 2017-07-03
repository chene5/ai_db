# -*- coding: utf-8 -*-
"""views.py
Routes and views for the Data Collector Flask web application.

The home page is the upload page, and requests like / and /index and /home
redirect to that page.

/upload: The upload page, where CSV files can be uploaded.

/download: The download page, where datasets can be downloaded.


@author: Eric
"""
import dblib
import uploader
import downloader
from flask import render_template, redirect, request
from application import application


@application.route('/index')
@application.route('/home')
def home():
    """Redirect to /"""
    return redirect('/')


@application.route('/upload', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
def upload():
    """Renders the home page, which is also the upload page."""
    if request.method == 'POST':
        if 'uploadData' in request.form:
            error = uploader.upload_file()
            print error
            if error:
                message = error
            else:
                message = 'Upload successful!'
            return render_template(
                'index.html',
                title='Upload data',
                message=message,
                )
    return render_template(
        'index.html',
        title='Upload data',
        message='Upload a CSV file')


@application.route('/download')
def download():
    """Render the download page, where users can download datasets."""
    title = 'Please select a dataset to download'
    message = None
    header = ['Table name', 'Filename']
    # table_names = dblib.get_table_names()
    # The template expects a table, so make each name its own row.
    # output = [[name] for name in table_names if name not in TABLE_EXCLUDES]
    output = dblib.get_all_table_info()
    if 'dataset' in request.args:
        dataset_name = request.args.get('dataset')
        print 'Dataset requested:', dataset_name
        if dataset_name:
            response = downloader.download_dataset(dataset_name)
            if response:
                return response
            else:
                message = 'Unable to retrieve dataset'
    return render_template(
        'download.html',
        header=header,
        title=title,
        output=output,
        message=message)


@application.errorhandler(404)
def page_not_found(error):
    """404 error handling for requests for unknown pages."""
    return render_template('page_not_found.html',
                           title="Sorry!",
                           message="The requested page couldn't be found."), \
        404
