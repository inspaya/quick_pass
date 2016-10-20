from __future__ import unicode_literals

from mock import patch, Mock
from services import QPServices


class TestQPServices(object):

    def test__get_environ_var(self):
        with patch('QPServices._get_environ_var') as mock_get_environ_var:
            mock_get_environ_var.return_value = 'test_ftp_user'
            qps = QPServices
