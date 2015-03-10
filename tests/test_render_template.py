import unittest
from jinja import Environment, DictLoader
from cloudplate.render import render_template, NoCloudletsError, MalformedTemplateError

cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n'),
             'paramed.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                              'Properties:\n'
                              '  Path: /\n'
                              '  Roles:\n'
                              '  - {{role}}\n')}


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
        template_def = ('paramed', {'parameters': {'role': 'DatRole'},
                                    'cloudlets': {'paramed': None}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'paramed': {'Type': 'AWS::IAM::InstanceProfile',
                                          'Properties': {
                                              'Path': '/',
                                              'Roles': ['DatRole']
                                          }}}}, render_template(self.jenv, template_def))

    def test_render_template_with_global_params_is_overridden_by_local_params(self):
        template_def = ('paramed', {'parameters': {'role': 'DatRole'},
                                    'cloudlets': {'paramed': {'parameters': {'role': 'MuhRole'}}}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'paramed': {'Type': 'AWS::IAM::InstanceProfile',
                                          'Properties': {
                                              'Path': '/',
                                              'Roles': ['MuhRole']
                                          }}}}, render_template(self.jenv, template_def))

    def test_render_template_with_two_cloudlets(self):
        template_def = ('paramed', {'cloudlets': {'paramed': {'parameters': {'role': 'MuhRole'}},
                                                  'plain': None}})
        self.assertEqual({'AWSTemplateFormatVersion': '2010-09-09',
                          'Resources': {
                              'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                        'Properties': {
                                            'Path': '/',
                                            'Roles': ['TheRole']
                                        }},
                              'paramed': {'Type': 'AWS::IAM::InstanceProfile',
                                          'Properties': {
                                              'Path': '/',
                                              'Roles': ['MuhRole']
                                          }}}}, render_template(self.jenv, template_def))


if __name__ == '__main__':
    unittest.main()
