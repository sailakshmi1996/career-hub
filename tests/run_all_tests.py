#!/usr/bin/env python3
"""
Test Suite Runner for Sai Lakshmi Elusuri Public Portfolio
Validates:
1. Public repo & dist isolation (zero private job-hunt files or +91 phone leaks)
2. Direction 1 Editorial Analytics Brief HTML/CSS/ARIA/WCAG contrast invariants
3. Canonical 2-page A4 PDF CV integrity & synchronization
4. Technical Showcase accuracy (DAX, Oracle SQL, Fabric PySpark MERGE)
5. Zero third-party trackers & IND endorsement presence
"""

import os
import sys
import unittest


def run_tests():
    start_dir = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print(f"✅ ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!")
        print("   - Zero private prep leaks in repo root or dist/")
        print("   - Direction 1 WCAG AA/AAA tokens & semantic landmarks verified")
        print("   - Canonical 2-page A4 PDF CV & OG assets verified")
        print("   - Technical Showcase DAX/SQL/PySpark patterns verified")
        print("=" * 60)
        return 0
    else:
        print(f"❌ TEST SUITE FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
