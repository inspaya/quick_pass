from __future__ import unicode_literals

from app import db


class Participant(db.Model):
    __tablename__ = 'tb_participant'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(36), nullable=False)
    lastname = db.Column(db.String(36), nullable=False)
    email = db.Column(db.String(36), unique=True, nullable=False)
    code = db.Column(db.String(36), unique=True, nullable=False)

    def __init__(self, firstname, lastname, email, code):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.code = code

    def __repr__(self):
        return '{firstname} {lastname} {email}'.format(
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email
        )
