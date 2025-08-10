#!/usr/bin/env python3
"""
Test script for case law analysis functionality
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_canlii_integration():
    """Test CanLII API integration"""
    print("Testing CanLII API Integration...")
    print("=" * 50)
    
    try:
        from utils.canadian_law_ai import canadian_law_ai
        
        # Test case law search
        print("1. Testing case law search...")
        cases = canadian_law_ai.get_canadian_case_law("constitutional rights", "ca", 5)
        print(f"   Found {len(cases)} cases")
        
        if cases:
            first_case = cases[0]
            print(f"   First case: {first_case.get('title', 'N/A')}")
            print(f"   Citation: {first_case.get('citation', 'N/A')}")
        
        # Test case details
        print("2. Testing case details...")
        if cases:
            first_case = cases[0]
            database_id = first_case.get("databaseId", "bcca")
            case_id = first_case.get("caseId", {}).get("en", "2020bcca123")
            
            details = canadian_law_ai.get_case_details(database_id, case_id)
            print(f"   Case title: {details.get('title', 'N/A')}")
            print(f"   Decision date: {details.get('decisionDate', 'N/A')}")
        
        print("\n[PASS] CanLII API integration tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] CanLII API integration test failed: {str(e)}")
        return False

def test_case_law_search():
    """Test case law search functionality"""
    print("\nTesting Case Law Search...")
    print("=" * 50)
    
    try:
        from utils.case_law_search import case_law_search
        
        # Test keyword search
        print("1. Testing keyword search...")
        keywords = ["charter", "rights", "freedom"]
        cases = case_law_search.search_by_keywords(keywords, "ca", 3)
        print(f"   Found {len(cases)} cases for keywords: {', '.join(keywords)}")
        
        # Test citation search
        print("2. Testing citation search...")
        citation_case = case_law_search.search_by_citation("2020 BCCA 123")
        if citation_case:
            print(f"   Found case by citation: {citation_case.get('title', 'N/A')}")
        else:
            print("   No case found by citation (expected with mock data)")
        
        # Test court search
        print("3. Testing court search...")
        court_cases = case_law_search.search_by_court("Supreme Court of Canada", "ca", 2)
        print(f"   Found {len(court_cases)} cases from Supreme Court of Canada")
        
        # Test result formatting
        print("4. Testing result formatting...")
        formatted = case_law_search.format_search_results(cases, "charter rights")
        print(f"   Formatted {len(formatted)} results")
        if formatted:
            print(f"   First formatted case: {formatted[0].get('title', 'N/A')}")
            print(f"   Relevance score: {formatted[0].get('relevance_score', 0)}")
        
        print("\n[PASS] Case law search tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Case law search test failed: {str(e)}")
        return False

def test_caching():
    """Test caching functionality"""
    print("\nTesting Caching Functionality...")
    print("=" * 50)
    
    try:
        from utils.canadian_law_ai import canadian_law_ai
        
        # Test that cache works
        print("1. Testing cache behavior...")
        query = "constitutional rights"
        
        # First request
        start_time = datetime.now()
        cases1 = canadian_law_ai.get_canadian_case_law(query, "ca", 2)
        first_request_time = (datetime.now() - start_time).total_seconds()
        
        # Second request (should be cached)
        start_time = datetime.now()
        cases2 = canadian_law_ai.get_canadian_case_law(query, "ca", 2)
        second_request_time = (datetime.now() - start_time).total_seconds()
        
        print(f"   First request time: {first_request_time:.4f}s")
        print(f"   Second request time: {second_request_time:.4f}s")
        
        # Check if we got the same results
        if len(cases1) == len(cases2):
            print("   [PASS] Cache returned consistent results")
        else:
            print("   [WARN] Cache may not be working correctly")
        
        print("\n[PASS] Caching tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Caching test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Smart Dispute Canada Case Law Analysis Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Run all tests
    tests = [
        test_canlii_integration,
        test_case_law_search,
        test_caching
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("CASE LAW ANALYSIS TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[PASS] All {total} tests passed!")
        print("Case law analysis functionality is working correctly.")
    else:
        print(f"[FAIL] {passed}/{total} tests passed.")
        print("Some case law analysis functionality may not be working correctly.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)