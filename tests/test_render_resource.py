import unittest
from jinja2 import DictLoader
from cloudforge.render import Renderer


resources = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n'),
             'vared.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - {{role}}\n')}


class RenderResourceTest(unittest.TestCase):
    renderer = Renderer(DictLoader(resources))

    def test_render_plain(self):
        resource_def = ('plain', None)
        self.assertEqual({'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                    'Properties': {
                                        'Path': '/',
                                        'Roles': ['TheRole']
                                    }}}, self.renderer.render_resource(resource_def))

    def test_render_named(self):
        resource_def = ('plain', {'name': 'MyName'})
        self.assertEqual({'MyName': {'Type': 'AWS::IAM::InstanceProfile',
                                     'Properties': {
                                         'Path': '/',
                                         'Roles': ['TheRole']
                                     }}}, self.renderer.render_resource(resource_def))

    def test_render_template(self):
        resource_def = ('abjqrml', {'template': 'plain.yaml'})
        self.assertEqual({'abjqrml': {'Type': 'AWS::IAM::InstanceProfile',
                                      'Properties': {
                                          'Path': '/',
                                          'Roles': ['TheRole']
                                      }}}, self.renderer.render_resource(resource_def))

    def test_render_params(self):
        resource_def = ('vared', {'variables': {'role': 'DatRole'}})
        self.assertEqual({'vared': {'Type': 'AWS::IAM::InstanceProfile',
                                    'Properties': {
                                        'Path': '/',
                                        'Roles': ['DatRole']
                                    }}}, self.renderer.render_resource(resource_def))


if __name__ == '__main__':
    unittest.main()
