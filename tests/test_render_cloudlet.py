import unittest
from jinja import Environment, DictLoader
from cloudplate.render import render_cloudlet


cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n')}


class RenderCloudletTest(unittest.TestCase):
    def test_render_plain(self):
        cloudlet_def = ('plain', None)
        jenv = Environment(loader=DictLoader(cloudlets))
        self.assertEqual({'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                    'Properties': {
                                        'Path': '/',
                                        'Roles': ['TheRole']
                                    }}}, render_cloudlet(jenv, cloudlet_def))


if __name__ == '__main__':
    unittest.main()
