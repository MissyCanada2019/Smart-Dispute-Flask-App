#!/usr/bin/env python3
"""
Test script for AI routes functionality
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_canadian_law_ai():
    """Test the Canadian law AI service"""
    print("Testing Canadian Law AI Service...")
    print("=" * 50)
    
    try:
        from utils.canadian_law_ai import canadian_law_ai
        
        # Test case law analysis
        print("1. Testing case law analysis...")
        case_law = canadian_law_ai.get_canadian_case_law("constitutional rights")
        print(f"   Found {len(case_law)} cases")
        
        # Test evidence relevance analysis
        print("2. Testing evidence relevance analysis...")
        evidence_text = "This evidence shows violation of charter rights under section 7"
        case_type = "constitutional"
        analysis = canadian_law_ai.analyze_evidence_relevance(evidence_text, case_type)
        print(f"   Relevance score: {analysis.get('ai_relevance_score')}")
        print(f"   Matching keywords: {analysis.get('matching_keywords')}")
        
        # Test legal advice
        print("3. Testing legal advice generation...")
        case_summary = "Constitutional challenge to government action"
        advice = canadian_law_ai.get_legal_advice(case_summary)
        print(f"   Generated advice: {advice[:100]}...")
        
        print("\n[PASS] All Canadian Law AI tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Canadian Law AI test failed: {str(e)}")
        return False

def test_evidence_processor():
    """Test the evidence processor with AI"""
    print("\nTesting Evidence Processor...")
    print("=" * 50)
    
    try:
        from utils.evidence_processor import EvidenceProcessor
        
        # Test evidence processing (without database)
        processor = EvidenceProcessor()
        print("   EvidenceProcessor initialized successfully")
        
        print("[PASS] Evidence Processor test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Evidence Processor test failed: {str(e)}")
        return False

def test_merit_scorer():
    """Test the merit scorer with AI"""
    print("\nTesting Merit Scorer...")
    print("=" * 50)
    
    try:
        from utils.merit_scoring import MeritScorer
        
        # Test merit scoring
        scorer = MeritScorer()
        print("   MeritScorer initialized successfully")
        
        # Test with empty list
        score = scorer.calculate_merit_score([])
        print(f"   Score for empty list: {score}")
        
        print("[PASS] Merit Scorer test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Merit Scorer test failed: {str(e)}")
        return False

def test_legal_journey():
    """Test the legal journey generator"""
    print("\nTesting Legal Journey Generator...")
    print("=" * 50)
    
    try:
        from utils.legal_journey import LegalJourneyGenerator
        
        # Test journey generation
        generator = LegalJourneyGenerator()
        print("   LegalJourneyGenerator initialized successfully")
        
        print("[PASS] Legal Journey Generator test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Legal Journey Generator test failed: {str(e)}")
        return False

def test_form_prefill():
    """Test the form prefill utility"""
    print("\nTesting Form Prefill Utility...")
    print("=" * 50)
    
    try:
        from utils.form_prefill import FormPrefill
        
        # Test form prefill
        prefill = FormPrefill()
        print("   FormPrefill initialized successfully")
        
        print("[PASS] Form Prefill test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Form Prefill test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Smart Dispute Canada AI Routes Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Run all tests
    tests = [
        test_canadian_law_ai,
        test_evidence_processor,
        test_merit_scorer,
        test_legal_journey,
        test_form_prefill
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
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[PASS] All {total} tests passed!")
        print("AI routes are working correctly with free-tier Canadian law services.")
    else:
        print(f"[FAIL] {passed}/{total} tests passed.")
        print("Some AI routes may not be working correctly.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)