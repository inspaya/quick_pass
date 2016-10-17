from __future__ import unicode_literals

import os
import uuid
import pysftp

from subprocess import check_call
from twilio.rest import TwilioRestClient


def _get_environ_var(var_name):
    return os.environ.get(var_name, None)


def _build_qr_code_and_url(select_attributes):
    """
    TODO: Move this method into a worker.
    Create a QR Code containing unique ID based on some criteria,
    upload to secure location and return image url
    """
    code = '{}'.format(str(uuid.uuid1()))
    code_filename = '{}{}'.format(code, '.png')
    code_text = '{}|{}'.format(code, select_attributes[0])
    code_generator_return = check_call(
        [
            _get_environ_var('CODE_GENERATOR_EXECUTABLE'),
            '-o',
            code_filename,
            code_text
        ]
    )

    # Upload image
    with pysftp.Connection(
        _get_environ_var('FTP_HOST'),
        username=_get_environ_var('FTP_USERNAME'),
        password=_get_environ_var('FTP_PASSWORD')
    ) as sftp:
        with sftp.cd(_get_environ_var('FTP_FOLDER')):
            sftp.put(code_filename)

    # Return image url
    if code_generator_return:
        image_url = _get_environ_var('BASE_MMS_URL') + code_filename
        return image_url
    else:
        return code_generator_return


def send_code_via_mms(participant):
    """
    Send code to participant via MMS
    """
    select_attributes = (participant.email,)

    try:
        client = TwilioRestClient(
            _get_environ_var('TWILIO_ACCOUNT_SID'),
            _get_environ_var('TWILIO_AUTH_TOKEN')
        )

        message = client.messages.create(
            body='Registration was successful. Your code is ',
            from_=_get_environ_var('SENT_FROM'),
            to=_get_environ_var('TEST_RECIPIENT'),
            media_url=_build_qr_code_and_url(select_attributes)
        )

        if message.error_code is None:
            return 'Success'
        return message.error_code
    except Exception as e:
        return e
