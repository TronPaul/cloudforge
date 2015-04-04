import unittest
import mock
import json
from jinja2 import DictLoader
from argparse import Namespace
from StringIO import StringIO
from cloudforge.render import Renderer
from cloudforge.cli import dump, DefinitionLookupError, StackLookupError
from .util import byteify

plain_stack = ('plain:\n'
               '  stacks:\n'
               '    my_stack:\n'
               '      resources:\n'
               '        plain:\n')

resources = {'plain.yaml': ('Type: AWS::IAM::InstanceProfile\n'
                            'Properties:\n'
                            '  Path: /\n'
                            '  Roles:\n'
                            '  - TheRole\n')}


class DumpTest(unittest.TestCase):
    @mock.patch('cloudforge.cli.make_renderer')
    @mock.patch('cloudforge.cli.open', create=True)
    def test_dump_template(self, mock_open, mock_renderer):
        mock_open.return_value.__enter__.return_value = StringIO(plain_stack)
        mock_renderer.return_value = Renderer(DictLoader(resources))
        args = Namespace(definition_name='plain', stack_name='my_stack', yamlfile='test.yaml')
        self.assertEqual(json.dumps({'AWSTemplateFormatVersion': '2010-09-09',
                                     'Resources': {
                                         'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                                   'Properties': {
                                                       'Path': '/',
                                                       'Roles': ['TheRole']
                                                   }}}}), dump(args))

    @mock.patch('cloudforge.cli.make_renderer')
    @mock.patch('cloudforge.cli.open', create=True)
    def test_dump_bad_definition_fails(self, mock_open, mock_renderer):
        mock_open.return_value.__enter__.return_value = StringIO(plain_stack)
        mock_renderer.return_value = Renderer(DictLoader(resources))
        args = Namespace(definition_name='fake', stack_name='my_stack', yamlfile='test.yaml')
        self.assertRaises(DefinitionLookupError, dump, args)

    @mock.patch('cloudforge.cli.make_renderer')
    @mock.patch('cloudforge.cli.open', create=True)
    def test_dump_bad_template_fails(self, mock_open, mock_renderer):
        mock_open.return_value.__enter__.return_value = StringIO(plain_stack)
        mock_renderer.return_value = Renderer(DictLoader(resources))
        args = Namespace(definition_name='plain', stack_name='fake_stack', yamlfile='test.yaml')
        self.assertRaises(StackLookupError, dump, args)


if __name__ == '__main__':
    unittest.main()
