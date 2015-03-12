import unittest
from cloudplate.cloudforge import order_templates


class OrderTemplatesTest(unittest.TestCase):
    def test_order_returns_all_templates_without_deps(self):
        def_ = {'cloudlets': {'fake': None}}
        templates = {'a': def_, 'b': def_}
        rv = order_templates(templates)
        self.assertEqual(2, len(rv))
        self.assertTrue(all([i in rv for i in templates.items()]))


if __name__ == '__main__':
    unittest.main()
