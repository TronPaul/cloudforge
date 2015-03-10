import unittest
from jinja import Environment, DictLoader
from cloudplate.render import render_template

cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n')}


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


if __name__ == '__main__':
    unittest.main()
