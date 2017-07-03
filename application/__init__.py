# -*- coding: utf-8 -*-
"""__init__.py
The flask application package.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


application = Flask(__name__)
application.config.from_object('config')

db = SQLAlchemy(application)
from application import views, models
