import unittest

class ReadDefinitionTest(unittest.TestCase):
    def test_read_plain(self):
        def_ = ('plain:\n'
                '  templates:\n'
                '    my_template:\n'
                '      cloudlets:\n'
                '        plain:\n')
