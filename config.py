# -*- coding: utf-8 -*-
"""config.py
Configurations for the Data Collector Flask app.

The database can be set up to use the AWS RDS service
or a local sqlite database file.


@author: Eric
"""
import os.path


basedir = os.path.abspath(os.path.dirname(__file__))

"""Use this to deploy to AWS RDS.
SQLALCHEMY_DATABASE_URI = \
    "mysql+pymysql://name:key@the.address.rds.amazonaws.com:3306/thedbname"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'aws_db_repository')
"""
# Use a local sqlite database.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'database_db_repository')

SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = \
    "!p/\x99\xe4\xfd.'\x0e\xc0\x18\xd1T@\x1c\xd7\x00\x15\x00\xd8\xeaRD\xce"
DEBUG = True
