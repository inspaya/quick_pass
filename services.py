from __future__ import unicode_literals

import os
import uuid

from ftplib import FTP_TLS
from subprocess import check_call
from twilio.rest import TwilioRestClient


def _get_environ_var(var_name):
    return os.environ.get(var_name, None)


def _upload_qr_code(code_filename):
    """
    TODO: Move to worker
    """
    with open(code_filename, 'rb') as fp:
        ftps = FTP_TLS(_get_environ_var('FTP_HOST'))
        ftps.login(_get_environ_var('FTP_USERNAME'), _get_environ_var('FTP_PASSWORD'))
        ftps.prot_p()
        ftps.cwd(_get_environ_var('FTP_DIRECTORY'))
        ftps.storbinary('STOR ' + code_filename, fp)
        ftps.quit()


def _build_qr_code_and_url(select_attributes):
    """
    TODO: Move this method into a worker.
    Create a QR Code containing unique ID based on some criteria,
    upload to secure location and return image url
    """
    try:
        code = '{}'.format(str(uuid.uuid1()))
        code_filename = '{}{}'.format(code, '.png')
        code_text = '{}|{}'.format(code, select_attributes[0])
        code_generator_return = check_call(
            [
                _get_environ_var('CODE_GENERATOR_EXECUTABLE'),
                '-o',
                _get_environ_var('GENERATED_CODES_DIRECTORY') + code_filename,
                code_text
            ]
        )

        # Upload image if generation succeeded
        if code_generator_return == 0:
            _upload_qr_code(code_filename)
            image_url = _get_environ_var('BASE_MMS_URL') + code_filename
            return image_url, code_filename
    except Exception as e:
        raise e


def send_code_via_mms(participant):
    """
    Send code to participant via MMS
    """
    select_attributes = (participant.email,)

    try:
        url, code_filename = _build_qr_code_and_url(select_attributes)

        client = TwilioRestClient(
            _get_environ_var('TWILIO_ACCOUNT_SID'),
            _get_environ_var('TWILIO_AUTH_TOKEN')
        )

        message = client.messages.create(
            body='Registration was successful. Your code is ',
            from_=_get_environ_var('SENT_FROM'),
            to=_get_environ_var('TEST_RECIPIENT'),
            media_url=url
        )

        if message.error_code is None:
            return code_filename
    except Exception as e:
        raise e
