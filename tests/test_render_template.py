import unittest
from jinja2 import Environment, DictLoader
from cloudplate.render import render_template, NoCloudletsError, MalformedTemplateError

cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
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
    jenv = Environment(loader=DictLoader(cloudlets))

    def test_render_simple_template(self):
        template_def = ('simple', {'cloudlets': {'plain': None}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['TheRole']
                                        }}}}, render_template(self.jenv, template_def))

    def test_render_template_without_cloudlets_fails(self):
        template_def = ('simple', {})
        self.assertRaises(NoCloudletsError, render_template, self.jenv, template_def)

    def test_render_template_with_empty_cloudlets_fails(self):
        template_def = ('simple', {'cloudlets': {}})
        self.assertRaises(NoCloudletsError, render_template, self.jenv, template_def)

    def test_render_template_with_bad_cloudlets_fails(self):
        template_def = ('simple', {'cloudlets': True})
        self.assertRaises(MalformedTemplateError, render_template, self.jenv, template_def)

    def test_render_template_with_global_params(self):
        template_def = ('vared', {'variables': {'role': 'DatRole'},
                                  'cloudlets': {'vared': None}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['DatRole']
                                        }}}}, render_template(self.jenv, template_def))

    def test_render_template_with_global_params_is_overridden_by_local_params(self):
        template_def = ('paramed', {'variables': {'role': 'DatRole'},
                                    'cloudlets': {'vared': {'variables': {'role': 'MuhRole'}}}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['MuhRole']
                                        }}}}, render_template(self.jenv, template_def))

    def test_render_template_with_two_cloudlets(self):
        template_def = ('vared', {'cloudlets': {'vared': {'variables': {'role': 'MuhRole'}},
                                                'plain': None}})
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
                                        }}}}, render_template(self.jenv, template_def))

    def test_render_template_with_resource_param(self):
        template_def = ('paramed_typed', {
            'parameters': {
                'VPC': {
                    'source': {
                        'template': 'vpc',
                        'type': 'resource'
                    },
                    'type': 'string',
                }
            },
            'cloudlets': {
                'typed': None
            }})
        self.maxDiff = None
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
                          }}, render_template(self.jenv, template_def))


if __name__ == '__main__':
    unittest.main()
