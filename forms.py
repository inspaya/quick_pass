from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class ParticipantForm(Form):
    firstname = StringField(
        'First Name',
        [DataRequired(message='Please enter a First Name')]
    )
    lastname = StringField(
        'Last Name',
        [DataRequired(message='Please enter a Last Name')]
    )
    email = StringField(
        'Email Address',
        [Email(), DataRequired(message='Please enter an Email Address')]
    )
