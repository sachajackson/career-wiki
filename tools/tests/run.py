#!/usr/bin/env python3
"""Run every test in the deterministic layer.

    python3 tools/tests/run.py

No dependencies, nothing to install. If this fails, do not ship a document --
the checks that catch a fabricated figure or a wrong-employer attribution are
the ones being tested here.
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(HERE, pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    n = result.testsRun
    bad = len(result.failures) + len(result.errors)
    print()
    if bad:
        print(f"{bad} of {n} checks FAILED. The deterministic layer is not trustworthy "
              f"until these pass.")
    else:
        print(f"All {n} checks passed. That means the checkers work -- "
              f"it does not mean any document is correct.")
    sys.exit(1 if bad else 0)
