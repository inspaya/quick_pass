from __future__ import unicode_literals

import os
import uuid

from ftplib import FTP_TLS
from subprocess import check_call
from collections import namedtuple

from boto3 import resource
from twilio.rest import TwilioRestClient

UploadMeta = namedtuple('UploadMeta', 'upload_handler base_mms_url')


def _get_environ_var(var_name):
    return os.environ.get(var_name, None)


def _upload_qr_code_s3(code_filename):
    s3 = resource('s3')

    bucket_handle = s3.Object(
        bucket_name=_get_environ_var('AWS_BUCKET_NAME'),
        key=code_filename
    )

    bucket_handle.put(
        Body=open(_get_environ_var('GENERATED_CODES_DIRECTORY') + code_filename, 'rb')
    )


def _upload_qr_code_ftp(code_filename):
    """
    TODO:
    1. Remove DRY code around code_fullpath
    """
    code_fullpath = _get_environ_var('GENERATED_CODES_DIRECTORY') + code_filename
    with open(code_fullpath, 'rb') as fp:
        ftps = FTP_TLS(_get_environ_var('FTP_HOST'))
        ftps.login(_get_environ_var('FTP_USERNAME'), _get_environ_var('FTP_PASSWORD'))
        ftps.prot_p()
        ftps.cwd(_get_environ_var('FTP_DIRECTORY'))
        ftps.storbinary('STOR ' + code_filename, fp)
        ftps.quit()


def _build_qr_code_and_url(select_attributes, upload_type='s3'):
    """
    Create a QR Code containing unique ID based on some criteria,
    upload to secure location and return image url
    """
    s3_meta = UploadMeta(
        upload_handler=_upload_qr_code_s3, base_mms_url=_get_environ_var('MMS_S3_URL')
    )

    ftp_meta = UploadMeta(
        upload_handler=_upload_qr_code_ftp, base_mms_url=_get_environ_var('MMS_FTP_URL')
    )

    UPLOAD_META = {
        'ftp': ftp_meta,
        's3': s3_meta
    }

    try:
        code = '{}'.format(str(uuid.uuid1()))
        code_filename = '{}{}'.format(code, '.png')
        code_fullpath = _get_environ_var('GENERATED_CODES_DIRECTORY') + code_filename
        code_generator_return = check_call(
            [
                _get_environ_var('CODE_GENERATOR_EXECUTABLE'),
                '-o',
                code_fullpath,
                code
            ]
        )

        # Upload image if generation succeeded
        if code_generator_return == 0:
            upload_type = UPLOAD_META[upload_type]
            upload_type.upload_handler(code_filename)
            image_url = upload_type.base_mms_url + code_filename
            return image_url, code
    except Exception as e:
        raise e


def send_code_via_mms(participant):
    """
    Send code to participant via MMS
    """
    select_attributes = (participant.email,)

    try:
        url, code = _build_qr_code_and_url(select_attributes)

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
            return code
    except Exception as e:
        raise e
