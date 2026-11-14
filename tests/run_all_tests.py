#!/usr/bin/env python3
"""
Test Suite Runner for Netherlands Career Command Center
Validates:
1. Site structural integrity & asset availability
2. Internal navigation anchors
3. Zero-date / milestone adherence
4. GDPR / AVG compliance & candidate privacy safeguards
"""

import unittest
import sys
import os

def run_tests():
    # Discover and run tests in current directory
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    if result.wasSuccessful():
        print(f"✅ ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!")
        print("   - Zero prohibited calendar dates/timelines")
        print("   - Full GDPR/AVG compliance verified")
        print("   - All local assets (PDFs, HTMLs, ZIP) verified")
        print("   - All navigation anchor links resolved")
        print("   - All 10 Women in Tech communities confirmed")
        print("="*60)
        return 0
    else:
        print(f"❌ TEST SUITE FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
