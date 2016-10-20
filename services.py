from __future__ import unicode_literals

import os
import uuid

from ftplib import FTP_TLS
from subprocess import check_call
from twilio.rest import TwilioRestClient


class QPServices(object):
    @staticmethod
    def _get_environ_var(var_name):
        return os.environ.get(var_name, None)

    @staticmethod
    def _upload_qr_code(code_filename):
        """
        TODO: Move to worker
        """
        with open(code_filename, 'rb') as fp:
            ftps = FTP_TLS(QPServices._get_environ_var('FTP_HOST'))
            ftps.login(QPServices._get_environ_var('FTP_USERNAME'), QPServices._get_environ_var('FTP_PASSWORD'))
            ftps.prot_p()
            ftps.cwd(QPServices._get_environ_var('FTP_DIRECTORY'))
            ftps.storbinary('STOR ' + code_filename, fp)
            ftps.quit()

    @staticmethod
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
                    QPServices._get_environ_var('CODE_GENERATOR_EXECUTABLE'),
                    '-o',
                    QPServices._get_environ_var('GENERATED_CODES_DIRECTORY') + code_filename,
                    code_text
                ]
            )

            # Upload image if generation succeeded
            if code_generator_return == 0:
                QPServices._upload_qr_code(code_filename)
                image_url = QPServices._get_environ_var('BASE_MMS_URL') + code_filename
                return image_url, code_filename
        except Exception as e:
            raise e

    def send_code_via_mms(self, participant):
        """
        Send code to participant via MMS
        """
        select_attributes = (participant.email,)

        try:
            url, code_filename = QPServices._build_qr_code_and_url(select_attributes)

            client = TwilioRestClient(
                QPServices._get_environ_var('TWILIO_ACCOUNT_SID'),
                QPServices._get_environ_var('TWILIO_AUTH_TOKEN')
            )

            message = client.messages.create(
                body='Registration was successful. Your code is ',
                from_=QPServices._get_environ_var('SENT_FROM'),
                to=QPServices._get_environ_var('TEST_RECIPIENT'),
                media_url=url
            )

            if message.error_code is None:
                return code_filename
        except Exception as e:
            raise e
