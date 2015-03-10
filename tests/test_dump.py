import unittest
import json
from argparse import Namespace
from cloudplate.cli import dump


class DumpTest(unittest.TestCase):
    def test_dump_template(self):
        args = Namespace(template='plain')
        self.assertEqual(json.dumps({'AWSTemplateFormatVersion': '2010-09-09',
                                     'Resources': {
                                         'plain': {'Type': 'AWS::IAM::InstanceProfile',
                                                   'Properties': {
                                                       'Path': '/',
                                                       'Roles': ['TheRole']
                                                   }}}}), dump(args))


if __name__ == '__main__':
    unittest.main()
