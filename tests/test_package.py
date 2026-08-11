import unittest

import timonelo


class PackageTest(unittest.TestCase):
    def test_version_is_defined(self) -> None:
        self.assertEqual(timonelo.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()

