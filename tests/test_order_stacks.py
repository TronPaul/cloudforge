import unittest
from cloudforge.forge import order_stacks, MissingDependencyError, CircularDependencyError


class OrderStacksTest(unittest.TestCase):
    def test_order_returns_all_stacks_without_deps(self):
        def_ = {'resources': {'fake': None}}
        stacks = {'a': def_, 'b': def_}
        rv = order_stacks(stacks)
        self.assertEqual(2, len(rv))
        self.assertTrue(all([i in rv for i in stacks.items()]))

    def test_order_with_missing_dep_fails(self):
        stacks = {
            'a': {
                'requires': ['c'],
                'resources': {'fake': None}
            },
            'b': {'resources': {'fake': None}}
        }
        self.assertRaises(MissingDependencyError, order_stacks, stacks)

    def test_order_with_simple_deps(self):
        stacks = {
            'a': {
                'requires': ['b'],
                'resources': {'fake': None}
            },
            'b': {'resources': {'fake': None}}
        }
        self.assertEqual([('b', stacks['b']), ('a', stacks['a'])],
                         order_stacks(stacks))

    def test_order_with_circular_deps(self):
        stacks = {
            'a': {
                'requires': ['b'],
                'resources': {'fake': None}
            },
            'b': {
                'requires': ['a'],
                'resources': {'fake': None}
            }
        }
        self.assertRaises(CircularDependencyError, order_stacks, stacks)

    def test_order_using_parameters(self):
        stacks = {
            'a': {
                'resources': {'fake': None}
            },
            'b': {
                'parameters': {
                    'thing': {
                        'source': {
                            'stack': 'a'
                        }
                    }
                },
                'resources': {'fake': None}
            }
        }
        self.assertEqual([('a', stacks['a']), ('b', stacks['b'])],
                         order_stacks(stacks))


if __name__ == '__main__':
    unittest.main()
