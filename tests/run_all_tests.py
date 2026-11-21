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
    start_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(start_dir)

    # Ensure local dist/ staging directory exists for test coverage on fresh clones & CI
    dist_dir = os.path.join(base_dir, "dist")
    dist_index = os.path.join(dist_dir, "index.html")
    if not os.path.exists(dist_index):
        import shutil
        os.makedirs(dist_dir, exist_ok=True)
        files_to_copy = [
            "index.html", "dutch-career-hub.html", "shared.css",
            "cv_power_bi_developer.html", "cv_bi_project_delivery.html", "resume.html",
            "cv_power_bi_developer.pdf", "cv_bi_project_delivery.pdf", "Sai_Lakshmi_Elusuri_Resume.pdf"
        ]
        for f in files_to_copy:
            src = os.path.join(base_dir, f)
            dst = os.path.join(dist_dir, f)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)

    # Discover and run tests in current directory
    loader = unittest.TestLoader()
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
