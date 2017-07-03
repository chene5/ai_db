# -*- coding: utf-8 -*-
"""models.py
Models for the flask application.
This is the index of the tables in the database.

"""
from application import db
TABLE_INDEX_NAME = 'tableIndex'


class TableIndex(db.Model):
    """This is the class that SQLAlchemy will use to create the table."""
    __tablename__ = TABLE_INDEX_NAME
    table_id = db.Column(db.Integer)
    table_name = db.Column(db.Text, primary_key=True)
    filename = db.Column(db.Text)

    def __repr__(self):
        message = 'Table name: {}, Filename: {}'.format(self.table_name,
                                                        self.filename)
        return message
