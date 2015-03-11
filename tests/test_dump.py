import unittest
import mock
import json
from jinja2 import DictLoader
from argparse import Namespace
from StringIO import StringIO
from cloudplate.render import Renderer
from cloudplate.cli import dump

plain_template = ('plain:\n'
                  '  templates:\n'
                  '    my_template:\n'
                  '      cloudlets:\n'
                  '        plain:\n')

cloudlets = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n')}


class DumpTest(unittest.TestCase):
    @mock.patch('cloudplate.cli.make_renderer')
    @mock.patch('cloudplate.cli.open', create=True)
    def test_dump_template(self, mock_open, mock_renderer):
        mock_open.return_value.__enter__.return_value = StringIO(plain_template)
        mock_renderer.return_value = Renderer(DictLoader(cloudlets))
        args = Namespace(definition_name='plain', template_name='my_template', yamlfile='test.yaml')
        self.assertEqual(json.dumps({'AWSTemplateFormatVersion': '2010-09-09',
                                     'Resources': {
                                         'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                                   'Properties': {
                                                       'Path': '/',
                                                       'Roles': ['TheRole']
                                                   }}}}), dump(args))


if __name__ == '__main__':
    unittest.main()
