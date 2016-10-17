from __future__ import unicode_literals

import os

from flask import Flask, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from forms import ParticipantForm

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

# We have to import after creating the db object
from models import *
from services import *


@app.route('/', methods=['GET'])
def index():
    participant_form = ParticipantForm(request.form)
    return render_template('index.html', form=participant_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    participant_form = ParticipantForm(request.form)
    if participant_form.validate_on_submit():
        # ensure participant doesn't exist already
        participant = Participant.query.filter_by(
            email=participant_form.email.data
        ).first()
        if participant:
            return 'Existing'

        try:
            participant = Participant(
                firstname=participant_form.firstname.data,
                lastname=participant_form.lastname.data,
                email=participant_form.email.data
            )

            db.session.add(participant)
            db.session.commit()

            # send QR Code
            send_code_via_mms(participant)
        except Exception as e:
            return e

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
