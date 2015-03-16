import logging
from mock import MagicMock, patch, sentinel
import boto.sts as sts
import boto.cloudformation as cf


def assume_role(region, role_arn, role_session_name, role_opts=None):
    sts_conn = sts.connect_to_region(region)
    if not role_opts:
        role_opts = {}
    assumed_role = sts_conn.assume_role(role_arn, role_session_name, **role_opts)
    return assumed_role.credentials


def connect_to_cf(region, role_arn=None, role_session_name=None, role_opts=None):
    connect_opts = {}
    if role_arn:
        if not role_session_name:
            role_session_name = 'cloudplate'
        creds = assume_role(region, role_arn, role_session_name, role_opts=role_opts)
        connect_opts['aws_access_key_id'] = creds.access_key
        connect_opts['aws_secret_access_key'] = creds.secret_key
        connect_opts['security_token'] = creds.session_token
    return cf.connect_to_region(region, **connect_opts)


def connect(definition):
    conn_opts = {}
    role = definition.get('role')
    if role:
        conn_opts['role_arn'] = role.pop('role_arn')
        conn_opts['role_session_name'] = role.pop('role_session_name')
        conn_opts['role_opts'] = role
    return connect_to_cf(definition['region'], **conn_opts)


class LoggingMock(MagicMock):
    def _get_child_mock(self, **kw):
        return LoggingMock(**kw)

    def _mock_call(_mock_self, *args, **kwargs):
        logging.info('{!r}: called with args={!r}, kwargs={!r}'.format(_mock_self, args, kwargs.items()))
        return super(LoggingMock, _mock_self)._mock_call(_mock_self, *args, **kwargs)


def dry_run_connection(definition):
    stsctr = LoggingMock()
    stsctr.return_value = LoggingMock(spec=sts.STSConnection)
    cfctr = LoggingMock()
    cfctr.return_value = LoggingMock(spec=cf.CloudFormationConnection)
    with patch('cloudplate.aws.cf') as mock_cf:
        with patch('cloudplate.aws.sts') as mock_sts:
            mock_sts.connect_to_region = stsctr
            mock_cf.connect_to_region = cfctr
            return connect(definition)