import unittest
import mock
from cloudplate.aws import dry_run_connection


class DryRunTest(unittest.TestCase):
    def test_connection_is_a_mock(self):
        rv = dry_run_connection({'region': 'us-east-1'})
        self.assertTrue(issubclass(type(rv), mock.MagicMock))


if __name__ == '__main__':
    unittest.main()
