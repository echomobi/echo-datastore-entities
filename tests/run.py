import unittest
import sys
import os


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) == 2 else "test_*"
    # Add main dir to path
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
    suite = unittest.loader.TestLoader().discover(os.path.dirname(__file__), prefix)
    result = unittest.runner.TextTestRunner(verbosity=2, buffer=True).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
