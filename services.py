from __future__ import unicode_literals

import os
from subprocess import check_output
from twilio import TwilioRestClient


def _get_environ_var(var_name):
    return os.environ.get(var_name, None)


def _build_qr_code_and_url(*select_attributes):
    """
    TODO: Move this method into a worker.
    Create a QR Code containing unique ID based on some criteria,
    upload to secure location and return image url
    """
    code_text = '{}|{}'.format(select_attributes[0], select_attributes[1])
    code_filename = check_output(
        [_get_environ_var('CODE_GENERATOR_EXECUTABLE'), code_text]
    )
    # Upload image
    # Return image url
    image_url = _get_environ_var('BASE_MMS_URL') + code_filename
    return image_url


def send_code_via_mms(participant):
    """
    Send code to participant via MMS
    """
    select_attributes = (participant.id, participant.email,)

    client = TwilioRestClient(
        _get_environ_var('TWILIO_ACCOUNT_SID'),
        _get_environ_var('TWILIO_AUTH_TOKEN')
    )

    message = client.messages.create(
        body='Registration was successful. Your code is ',
        from_=_get_environ_var('SENT_FROM'),
        to=participant.phone,
        media_url=_build_qr_code_and_url(select_attributes)
    )

    if message['error_code'] is None:
        return 'Success'

    return 'Failed'
