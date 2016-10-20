from __future__ import unicode_literals

import os

from flask import Flask, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from worker import conn

from forms import ParticipantForm

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
q = Queue(connection=conn)

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
            q.enqueue_call(func=send_code_via_mms, args=(participant,), result_ttl=500)
        except Exception as e:
            # return friendly message based on Exception raised internally
            return 'Failed'

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
