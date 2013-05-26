from core.configuration import Configuration

import os
import unittest


class ConfigurationTest(unittest.TestCase):
    def test_initial_setup(self):
        if not os.path.exists(os.path.join(os.path.expanduser("~"), ".kissync")):
            os.makedirs(os.path.join(os.path.expanduser("~"), ".kissync"))
        Configuration(os.path.join(os.path.expanduser("~"), ".kissync", "configuration.cfg"))


if __name__ == '__main__':
    unittest.main()
