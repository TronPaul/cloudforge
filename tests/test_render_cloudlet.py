import unittest
from jinja import Environment, DictLoader
from cloudplate.render import render_cloudlet


cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n'),
             'vared.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - {{role}}\n')}


class RenderCloudletTest(unittest.TestCase):
    jenv = Environment(loader=DictLoader(cloudlets))

    def test_render_plain(self):
        cloudlet_def = ('plain', None)
        self.assertEqual({'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                    'Properties': {
                                        'Path': '/',
                                        'Roles': ['TheRole']
                                    }}}, render_cloudlet(self.jenv, cloudlet_def))

    def test_render_named(self):
        cloudlet_def = ('plain', {'name': 'MyName'})
        self.assertEqual({'MyName': {'Type': 'AWS::IAM::InstanceProfile',
                                     'Properties': {
                                         'Path': '/',
                                         'Roles': ['TheRole']
                                     }}}, render_cloudlet(self.jenv, cloudlet_def))

    def test_render_template(self):
        cloudlet_def = ('abjqrml', {'template': 'plain.yaml'})
        self.assertEqual({'abjqrml': {'Type': 'AWS::IAM::InstanceProfile',
                                      'Properties': {
                                          'Path': '/',
                                          'Roles': ['TheRole']
                                      }}}, render_cloudlet(self.jenv, cloudlet_def))

    def test_render_params(self):
        cloudlet_def = ('vared', {'variables': {'role': 'DatRole'}})
        self.assertEqual({'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                    'Properties': {
                                        'Path': '/',
                                        'Roles': ['DatRole']
                                    }}}, render_cloudlet(self.jenv, cloudlet_def))


if __name__ == '__main__':
    unittest.main()
