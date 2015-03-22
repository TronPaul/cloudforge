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
             'vared.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - {{role}}\n'),
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
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
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
    def test_forge_stack(self):
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
        forge.watcher = mock.MagicMock()
        forge.forge_stack('simple', {'cloudlets': {'simple': None}})
        conn.create_stack.assert_called_once_with('simple',
                                                  template_body=body, parameters=None)
        self.assertFalse(conn.describe_stacks.called)
        self.assertFalse(conn.describe_stack_resources.called)

    def test_forge_stack_with_variables(self):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        body = {'AWSTemplateFormatVersion': '2010-09-09',
                'Resources': {
                    'vared': {'Type': 'AWS::IAM::InstanceProfile',
                              'Properties': {
                                  'Path': '/',
                                  'Roles': ['DatRole']
                              }}}}
        r = make_renderer(cloudlets)
        forge = Forge(conn, r)
        forge.watcher = mock.MagicMock()
        forge.forge_stack('vared',
                             {'variables': {'role': 'DatRole'},
                              'cloudlets': {'vared': None}})
        args, kwargs = conn.create_stack.call_args
        self.assertEqual(1, conn.create_stack.call_count)
        self.assertEqual(('vared',), args)
        self.assertEqual(body, byteify(json.loads(kwargs['template_body'])))
        self.assertTrue(kwargs['parameters'] is None)
        self.assertFalse(conn.describe_stacks.called)
        self.assertFalse(conn.describe_stack_resources.called)

    def test_forge_stack_with_params(self):
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
        forge.watcher = mock.MagicMock()
        forge.forge_stack('params', {
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
        conn = mock.MagicMock(spec=CloudFormationConnection)
        body = {'AWSTemplateFormatVersion': '2010-09-09',
                'Resources': {
                    'simple': {
                        'Type': 'AWS::IAM::InstanceProfile',
                        'Properties': {
                            'Path': '/',
                            'Roles': ['TheRole']
                        }}}}
        r = make_renderer(cloudlets)
        forge = Forge(conn, r)
        forge.watcher = mock.MagicMock()
        forge.forge_definition('plain', {'stacks': {
            'plain': {'cloudlets': {'simple': None}}
        }})
        args, kwargs = conn.create_stack.call_args
        self.assertEqual(1, conn.create_stack.call_count)
        self.assertEqual(('plain',), args)
        self.assertEqual(body, byteify(json.loads(kwargs['template_body'])))
        self.assertTrue(kwargs['parameters'] is None)
        self.assertFalse(conn.describe_stacks.called)
        self.assertFalse(conn.describe_stack_resources.called)

    def test_forge_definition_with_multi_stacks(self):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        body = {'AWSTemplateFormatVersion': '2010-09-09',
                'Resources': {
                    'simple': {
                        'Type': 'AWS::IAM::InstanceProfile',
                        'Properties': {
                            'Path': '/',
                            'Roles': ['TheRole']
                        }}}}
        r = make_renderer(cloudlets)
        forge = Forge(conn, r)
        forge.watcher = mock.MagicMock()
        forge.forge_definition('plain', {'stacks': {
            'plain': {'cloudlets': {'simple': None}},
            'plain2': {'cloudlets': {'simple': None}}
        }})
        self.assertEqual(2, conn.create_stack.call_count)
        call1, call2 = conn.create_stack.call_args_list
        self.assertEqual(('plain',), call1[0])
        self.assertEqual(('plain2',), call2[0])
        self.assertEqual(body, json.loads(call1[1]['template_body']))
        self.assertEqual(body, json.loads(call2[1]['template_body']))
        self.assertTrue(call1[1]['parameters'] is None)
        self.assertTrue(call2[1]['parameters'] is None)


if __name__ == '__main__':
    unittest.main()
