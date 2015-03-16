import unittest
import mock
import json
from boto.cloudformation import CloudFormationConnection
from jinja2 import DictLoader
from cloudforge.forge import Forge
from cloudforge.render import Renderer

cloudlets = {'simple.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                             'Properties:\n'
                             '  Path: /\n'
                             '  Roles:\n'
                             '  - TheRole\n'),
             'typed.yaml': ('Type: AWS::EC2::SecurityGroup\n'
                            'Properties:\n'
                            '  VpcId:\n'
                            '    Ref: VPC\n'
                            '  SecurityGroupEgress:\n'
                            '    - IpProtocol: "-1"\n'
                            '      FromPort: "0"\n'
                            '      ToPort: "65535"\n'
                            '      CidrIp: 0.0.0.0/0')}


def make_renderer(d):
    return Renderer(DictLoader(d))


# Not asserting on unicode input
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def mock_resource_id(mock_conn, value):
    mock_conn.describe_stack_resource.return_value = {
        'DescribeStackResourceResponse': {
            'DescribeStackResourceResult': {
                'StackResourceDetail': {
                    'PhysicalResourceId': value
                }
            }
        }
    }


class ForgeTest(unittest.TestCase):
    def test_forge_template(self):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        body = json.dumps({'AWSTemplateFormatVersion': '2010-09-09',
                           'Resources': {
                               'simple': {
                                   'Type': 'AWS::IAM::InstanceProfile',
                                   'Properties': {
                                       'Path': '/',
                                       'Roles': ['TheRole']
                                   }}}})
        r = make_renderer(cloudlets)
        forge = Forge(conn, r)
        forge.forge_template('simple', {'cloudlets': {'simple': None}})
        conn.create_stack.assert_called_once_with('simple',
                                                  template_body=body, parameters=None)
        self.assertFalse(conn.describe_stacks.called)
        self.assertFalse(conn.describe_stack_resources.called)

    def test_forge_template_with_variables(self):
        pass

    def test_forge_template_with_params(self):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        mock_resource_id(conn, 'vpc-12345')
        body = {'AWSTemplateFormatVersion': '2010-09-09',
                'Parameters': {
                    'VPC': {
                        'Type': 'String'
                    }
                },
                'Resources': {
                    'typed': {
                        'Type': 'AWS::EC2::SecurityGroup',
                        'Properties': {
                            'VpcId': {'Ref': 'VPC'},
                            'SecurityGroupEgress': [
                                {'IpProtocol': '-1', 'FromPort': '0', 'ToPort': '65535',
                                 'CidrIp': '0.0.0.0/0'}
                            ]
                        }
                    }
                }}
        r = make_renderer(cloudlets)
        forge = Forge(conn, r)
        forge.forge_template('params', {
            'parameters': {'VPC': {'source': {'stack': 'vpc', 'type': 'resource'}, 'type': 'string'}},
            'cloudlets': {'typed': None}})
        args, kwargs = conn.create_stack.call_args
        self.assertEqual(1, conn.create_stack.call_count)
        self.assertEqual(('params',), args)
        self.assertEqual(body, byteify(json.loads(kwargs['template_body'])))
        self.assertEqual([('VPC', 'vpc-12345')], kwargs['parameters'])
        self.assertFalse(conn.describe_stacks.called)
        conn.describe_stack_resource.assert_called_once_with('vpc', 'VPC')

    def test_forge_definition(self):
        pass

    def test_forge_definition_with_variables(self):
        pass

    def test_forge_definition_with_multi_templates(self):
        pass


if __name__ == '__main__':
    unittest.main()