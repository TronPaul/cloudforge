import boto.sts as sts
import boto.cloudformation as cf


def assume_role(region, role_arn, role_session_name, role_opts=None):
    sts_conn = sts.connect_to_region(region)
    if not role_opts:
        role_opts = {}
    assumed_role = sts_conn.assume_role(role_arn, role_session_name, **role_opts)
    return assumed_role.credentials


def connect_to_cf(region, role_arn=None, role_sesion_name=None, role_opts=None):
    connect_opts = {}
    if role_arn:
        if not role_sesion_name:
            role_sesion_name = 'cloudplate'
        creds = assume_role(region, role_arn, role_sesion_name, role_opts=role_opts)
        connect_opts['aws_access_key_id'] = creds.access_key
        connect_opts['aws_secret_access_key'] = creds.secret_key
        connect_opts['security_token'] =  creds.sesion_token
    return cf.connect_to_region(region, **connect_opts)