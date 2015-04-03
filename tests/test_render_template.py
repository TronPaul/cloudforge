import json
import unittest
import mock
from jinja2 import DictLoader
from StringIO import StringIO
from cloudforge.render import Renderer, NoResourcesError, MalformedTemplateError
from .util import byteify

resources = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
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


class RenderTemplateTest(unittest.TestCase):
    renderer = Renderer(DictLoader(resources))

    def test_render_simple_template(self):
        stack_def = {'resources': {'plain': None}}
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['TheRole']
                                        }}}}, self.renderer.render_template(stack_def))

    def test_render_template_without_resources_fails(self):
        stack_def = {}
        self.assertRaises(NoResourcesError, self.renderer.render_template, stack_def)

    def test_render_template_with_empty_resources_fails(self):
        stack_def = {'resources': {}}
        self.assertRaises(NoResourcesError, self.renderer.render_template, stack_def)

    def test_render_template_with_bad_resources_fails(self):
        stack_def = {'resources': True}
        self.assertRaises(MalformedTemplateError, self.renderer.render_template, stack_def)

    def test_render_template_with_global_params(self):
        stack_def = {'variables': {'role': 'DatRole'},
                     'resources': {'vared': None}}
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['DatRole']
                                        }}}}, self.renderer.render_template(stack_def))

    def test_render_template_with_global_params_is_overridden_by_local_params(self):
        stack_def = {'variables': {'role': 'DatRole'},
                     'resources': {'vared': {'variables': {'role': 'MuhRole'}}}}
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['MuhRole']
                                        }}}}, self.renderer.render_template(stack_def))

    def test_render_template_with_two_resources(self):
        stack_def = {'resources': {'vared': {'variables': {'role': 'MuhRole'}},
                                   'plain': None}}
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['TheRole']
                                        }},
                              'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['MuhRole']
                                        }}}}, self.renderer.render_template(stack_def))

    def test_render_template_with_resource_param(self):
        stack_def = {
            'parameters': {
                'VPC': {
                    'source': {
                        'stack': 'vpc',
                        'type': 'resource'
                    },
                    'type': 'String',
                }
            },
            'resources': {
                'typed': None
            }
        }
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
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
                          }}, self.renderer.render_template(stack_def))

    @mock.patch('cloudforge.render.open', create=True)
    def test_render_template_with_resource_chunk(self, mock_open):
        plain_stack = json.dumps({
            'plain': {'Type': 'AWS::IAM::InstanceProfile',
                      'Properties': {
                          'Path': '/',
                          'Roles': ['TheRole']
                      }}})
        mock_open.return_value.__enter__.return_value = StringIO(plain_stack)
        stack_def = {'resource_chunk': 'resources.json'}
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['TheRole']
                                        }}}}, byteify(self.renderer.render_template(stack_def)))


if __name__ == '__main__':
    unittest.main()
