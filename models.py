from __future__ import unicode_literals

from app import db


class Participant(db.Model):
    __tablename__ = 'tb_participant'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True)

    def __init__(self, firstname, lastname, email):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email

    def __repr__(self):
        return '{firstname} {lastname} {email}'.format(
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email
        )
