import unittest
import mock
from cloudforge.forge import build_parameters
from collections import namedtuple

KeyValue = namedtuple('KeyValue', ['key', 'value'])


class MyTestCase(unittest.TestCase):
    def test_local_parameters(self):
        params = {
            'thing': '1',
            'otherThing': 2
        }
        self.assertEqual([('thing', '1',), ('otherThing', 2)],
                         build_parameters(mock.MagicMock(), params))

    def test_remote_resource_parameters(self):
        params = {
            'thing': {
                'source': {
                    'stack': 'test',
                    'type': 'resource'
                }
            }
        }
        conn = mock.MagicMock()
        rv = mock.MagicMock(spec=dict)
        conn.describe_stack_resource.return_value = rv
        resp = mock.MagicMock(spec=dict)
        rv.__getitem__.return_value = resp
        res_result = mock.MagicMock(spec=dict)
        resp.__getitem__.return_value = res_result
        res_detail = mock.MagicMock(spec=dict)
        res_result.__getitem__.return_value = res_detail
        res_detail.__getitem__.return_value = 'vpc-12345'
        self.assertEqual([('thing', 'vpc-12345')], build_parameters(conn, params))

    def test_remote_parameter_parameters(self):
        params = {
            'thing': {
                'source': {
                    'stack': 'test',
                    'type': 'parameter'
                }
            }
        }
        conn = mock.MagicMock()
        conn.describe_stacks.return_value.__getitem__.return_value.parameters = [KeyValue('abc', 'nope'), KeyValue('thing', '10.0.0.0/16')]
        self.assertEqual([('thing', '10.0.0.0/16')], build_parameters(conn, params))

    def test_remote_output_parameters(self):
        params = {
            'thing': {
                'source': {
                    'stack': 'test',
                    'type': 'output'
                }
            }
        }
        conn = mock.MagicMock()
        conn.describe_stacks.return_value.__getitem__.return_value.outputs = [KeyValue('abc', 'nope'), KeyValue('thing', '10.0.0.0/16')]
        self.assertEqual([('thing', '10.0.0.0/16')], build_parameters(conn, params))



if __name__ == '__main__':
    unittest.main()
