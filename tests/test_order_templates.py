import unittest
from cloudplate.cloudforge import order_templates, MissingDependencyError, CircularDependencyError


class OrderTemplatesTest(unittest.TestCase):
    def test_order_returns_all_templates_without_deps(self):
        def_ = {'cloudlets': {'fake': None}}
        templates = {'a': def_, 'b': def_}
        rv = order_templates(templates)
        print rv
        self.assertEqual(2, len(rv))
        self.assertTrue(all([i in rv for i in templates.items()]))

    def test_order_with_missing_dep_fails(self):
        templates = {
            'a': {
                'requires': ['c'],
                'cloudlets': {'fake': None}
            },
            'b': {'cloudlets': {'fake': None}}
        }
        self.assertRaises(MissingDependencyError, order_templates, templates)

    def test_order_with_simple_deps(self):
        templates = {
            'a': {
                'requires': ['b'],
                'cloudlets': {'fake': None}
            },
            'b': {'cloudlets': {'fake': None}}
        }
        self.assertEqual([('b', templates['b']), ('a', templates['a'])],
                         order_templates(templates))

    def test_order_with_circular_deps(self):
        templates = {
            'a': {
                'requires': ['b'],
                'cloudlets': {'fake': None}
            },
            'b': {
                'requires': ['a'],
                'cloudlets': {'fake': None}
            }
        }
        self.assertRaises(CircularDependencyError, order_templates, templates)

    def test_order_using_parameters(self):
        templates = {
            'a': {
                'cloudlets': {'fake': None}
            },
            'b': {
                'parameters': {
                    'thing': {
                        'source': {
                            'template': 'a'
                        }
                    }
                },
                'cloudlets': {'fake': None}
            }
        }
        self.assertEqual([('a', templates['a']), ('b', templates['b'])],
                         order_templates(templates))


if __name__ == '__main__':
    unittest.main()
