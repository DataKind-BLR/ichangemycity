import unittest
from dedupe import common

class TestConf(unittest.TestCase):
	def test_not_null(self):
		self.assertTrue(common.conf is not None)

if __name__ == '__main__':
    unittest.main()