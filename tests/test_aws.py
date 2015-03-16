import unittest
import mock
from boto.sts.credentials import Credentials, AssumedRole
from cloudforge import aws


class MyTestCase(unittest.TestCase):
    @mock.patch('cloudforge.aws.sts.connect_to_region')
    def test_assume_role(self, ctr_mock):
        region = 'us-east-1'
        role_arn = 'fake-role-arn'
        session_name = 'my-session'
        opts = {'opt1': True}
        conn = mock.MagicMock()
        ctr_mock.return_value = conn
        aws.assume_role(region, role_arn, session_name, opts)
        ctr_mock.assert_called_once_with(region)
        conn.assume_role.assert_called_once_with(role_arn, session_name, **opts)

    @mock.patch('cloudforge.aws.cf.connect_to_region')
    def test_connect_wo_role(self, ctr_mock):
        region = 'us-east-1'
        defn = {
            'region': region
        }
        aws.connect(defn)
        ctr_mock.assert_called_once_with(region)

    @mock.patch('cloudforge.aws.cf.connect_to_region')
    @mock.patch('cloudforge.aws.sts.connect_to_region')
    def test_connect_with_role(self, stsctr_mock, cfctr_mock):
        region = 'us-east-1'
        defn = {
            'region': region,
            'role': {
                'role_arn': 'fake-role-arn',
                'role_session_name': 'my-session',
                'role_opts': {
                    'duration': 1800
                }
            }
        }
        sts_conn = mock.MagicMock()
        stsctr_mock.return_value = sts_conn
        creds = Credentials()
        role = AssumedRole(credentials=creds)
        creds.access_key = 'access_key'
        creds.secret_key = 'secret_key'
        creds.session_token = 'session_token'
        sts_conn.assume_role.return_value = role
        aws.connect(defn)
        stsctr_mock.assert_called_once_with(region)
        cfctr_mock.assert_called_once_with(region, aws_access_key_id='access_key', aws_secret_access_key='secret_key',
                                           security_token='session_token')


if __name__ == '__main__':
    unittest.main()
