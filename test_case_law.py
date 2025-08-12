#!/usr/bin/env python3
"""
Test script for case law analysis functionality using the unittest framework.
"""

import sys
import os
import unittest
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestCaseLaw(unittest.TestCase):
    """Unit tests for case law functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        print("=" * 60)
        print("Starting Smart Dispute Canada Case Law Analysis Tests")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 60)

    def test_canlii_integration(self):
        """Test CanLII API integration."""
        print("\nTesting CanLII API Integration...")
        from utils.canadian_law_ai import canadian_law_ai

        # Test case law search
        print("  1. Testing case law search...")
        cases = canadian_law_ai.get_canadian_case_law("constitutional rights", "ca", 5)
        self.assertGreater(len(cases), 0, "Should find at least one case for 'constitutional rights'")
        print(f"     Found {len(cases)} cases.")

        first_case = cases[0]
        self.assertIn('title', first_case)
        self.assertIn('citation', first_case)
        print(f"     First case: {first_case.get('title', 'N/A')}")

        # Test case details
        print("  2. Testing case details...")
        database_id = first_case.get("databaseId")
        case_id = first_case.get("caseId", {}).get("en")
        self.assertIsNotNone(database_id, "Database ID should exist in case data")
        self.assertIsNotNone(case_id, "Case ID should exist in case data")

        details = canadian_law_ai.get_case_details(database_id, case_id)
        self.assertIsNotNone(details, "Should retrieve case details")
        self.assertIn('title', details)
        print(f"     Case title: {details.get('title', 'N/A')}")
        print("  [PASS] CanLII API integration test passed!")

    def test_case_law_search(self):
        """Test case law search functionality."""
        print("\nTesting Case Law Search...")
        from utils.case_law_search import case_law_search

        # Test keyword search
        print("  1. Testing keyword search...")
        keywords = ["charter", "rights", "freedom"]
        cases = case_law_search.search_by_keywords(keywords, "ca", 3)
        self.assertIsInstance(cases, list)
        print(f"     Found {len(cases)} cases for keywords: {', '.join(keywords)}")

        # Test citation search
        print("  2. Testing citation search...")
        citation_case = case_law_search.search_by_citation("2020 BCCA 123")
        if citation_case:
            print(f"     Found case by citation: {citation_case.get('title', 'N/A')}")
        else:
            print("     No case found by citation (may be expected with mock data)")

        # Test court search
        print("  3. Testing court search...")
        court_cases = case_law_search.search_by_court("Supreme Court of Canada", "ca", 2)
        self.assertIsInstance(court_cases, list)
        print(f"     Found {len(court_cases)} cases from Supreme Court of Canada")

        # Test result formatting
        print("  4. Testing result formatting...")
        formatted = case_law_search.format_search_results(cases, "charter rights")
        self.assertEqual(len(formatted), len(cases))
        if formatted:
            self.assertIn('relevance_score', formatted[0])
            print(f"     First formatted case has relevance score: {formatted[0].get('relevance_score', 0)}")
        print("  [PASS] Case law search test passed!")

    def test_caching(self):
        """Test caching functionality."""
        print("\nTesting Caching Functionality...")
        from utils.canadian_law_ai import canadian_law_ai

        # Test that cache works
        print("  1. Testing cache behavior...")
        query = "constitutional rights"

        # First request
        start_time = datetime.now()
        cases1 = canadian_law_ai.get_canadian_case_law(query, "ca", 2)
        first_request_time = (datetime.now() - start_time).total_seconds()

        # Second request (should be cached)
        start_time = datetime.now()
        cases2 = canadian_law_ai.get_canadian_case_law(query, "ca", 2)
        second_request_time = (datetime.now() - start_time).total_seconds()

        print(f"     First request time: {first_request_time:.4f}s")
        print(f"     Second request time: {second_request_time:.4f}s")

        self.assertEqual(len(cases1), len(cases2), "Cache should return consistent results")
        self.assertLess(second_request_time, first_request_time, "Cached request should be faster")
        print("  [PASS] Caching test passed!")

if __name__ == "__main__":
    unittest.main()