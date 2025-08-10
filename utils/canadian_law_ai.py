"""
Canadian Law AI Service
Provides free-tier AI functionality for Canadian legal analysis
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class CanadianLawAIService:
    """AI service for Canadian law using free resources"""
    
    def __init__(self):
        # Free Canadian legal databases
        self.canlii_api_base = "https://api.canlii.org/v1"
        self.canlii_api_key = "YOUR_FREE_API_KEY"  # Free tier key
        
        # Simple in-memory cache for case law results
        self.case_law_cache = {}
        self.case_details_cache = {}
        self.cache_expiry = 3600  # 1 hour in seconds
        
        # Canadian law keywords for relevance scoring
        self.canadian_law_keywords = {
            "constitutional": ["charter", "constitution", "rights", "freedom", "democracy"],
            "criminal": ["criminal code", "offence", "guilty", "sentence", "act"],
            "civil": ["tort", "contract", "property", "family", "employment"],
            "administrative": ["tribunal", "review", "appeal", "decision", "regulation"],
            "provincial": ["province", "municipal", "by-law", "ordinance"]
        }
    
    def analyze_case_relevance(self, case_text: str, keywords: List[str]) -> Dict:
        """
        Analyze case relevance based on keywords
        Returns relevance score and matching terms
        """
        matches = []
        case_lower = case_text.lower()
        
        for keyword in keywords:
            if keyword.lower() in case_lower:
                matches.append(keyword)
        
        # Calculate relevance score (0-100)
        relevance_score = min(100, len(matches) * 20)  # Max 100 points
        
        return {
            "relevance_score": relevance_score,
            "matching_keywords": matches,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def get_canadian_case_law(self, query: str, jurisdiction: str = "ca", limit: int = 10) -> List[Dict]:
        """
        Get Canadian case law using free CanLII API
        Note: This requires a free API key from CanLII
        """
        try:
            # Create cache key
            cache_key = f"{jurisdiction}:{query}:{limit}"
            
            # Check if result is in cache and not expired
            if cache_key in self.case_law_cache:
                cached_result, timestamp = self.case_law_cache[cache_key]
                if (datetime.utcnow() - timestamp).total_seconds() < self.cache_expiry:
                    print("Returning cached case law results")
                    return cached_result
            
            # Check if API key is configured
            if not self.canlii_api_key or self.canlii_api_key == "YOUR_FREE_API_KEY":
                print("CanLII API key not configured, returning mock data")
                # Return mock data if no API key
                mock_cases = [
                    {
                        "databaseId": "bcca",
                        "caseId": {"en": "2020bcca123"},
                        "title": "Sample v. Example",
                        "citation": "2020 BCCA 123",
                        "date": "2020-05-15"
                    },
                    {
                        "databaseId": "scc",
                        "caseId": {"en": "2019scc456"},
                        "title": "Test v. Demo",
                        "citation": "2019 SCC 456",
                        "date": "2019-11-30"
                    }
                ]
                
                # Cache the result
                self.case_law_cache[cache_key] = (mock_cases, datetime.utcnow())
                return mock_cases
            
            # Make request to CanLII search API
            search_url = f"{self.canlii_api_base}/search/{jurisdiction}"
            params = {
                "apiKey": self.canlii_api_key,
                "q": query,
                "resultCount": limit
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            cases = data.get("results", [])
            
            # Format cases for consistent return structure
            formatted_cases = []
            for case in cases:
                formatted_case = {
                    "databaseId": case.get("databaseId"),
                    "caseId": case.get("caseId"),
                    "title": case.get("title", ""),
                    "citation": case.get("citation", ""),
                    "date": case.get("decisionDate", "")
                }
                formatted_cases.append(formatted_case)
            
            # Cache the result
            self.case_law_cache[cache_key] = (formatted_cases, datetime.utcnow())
            
            return formatted_cases
            
        except Exception as e:
            print(f"Error fetching case law from CanLII: {str(e)}")
            # Return mock data as fallback
            mock_cases = [
                {
                    "databaseId": "bcca",
                    "caseId": {"en": "2020bcca123"},
                    "title": "Sample v. Example",
                    "citation": "2020 BCCA 123",
                    "date": "2020-05-15"
                },
                {
                    "databaseId": "scc",
                    "caseId": {"en": "2019scc456"},
                    "title": "Test v. Demo",
                    "citation": "2019 SCC 456",
                    "date": "2019-11-30"
                }
            ]
            return mock_cases
    
    def get_case_details(self, database_id: str, case_id: str) -> Dict:
        """
        Get detailed case information from CanLII
        """
        try:
            # Create cache key
            cache_key = f"{database_id}:{case_id}"
            
            # Check if result is in cache and not expired
            if cache_key in self.case_details_cache:
                cached_result, timestamp = self.case_details_cache[cache_key]
                if (datetime.utcnow() - timestamp).total_seconds() < self.cache_expiry:
                    print("Returning cached case details")
                    return cached_result
            
            # Check if API key is configured
            if not self.canlii_api_key or self.canlii_api_key == "YOUR_FREE_API_KEY":
                print("CanLII API key not configured, returning mock data")
                mock_details = {
                    "title": "Sample Case Title",
                    "citation": "2020 BCCA 123",
                    "decisionDate": "2020-05-15",
                    "jurisdiction": "British Columbia",
                    "summary": "This is a sample case summary for demonstration purposes."
                }
                
                # Cache the result
                self.case_details_cache[cache_key] = (mock_details, datetime.utcnow())
                return mock_details
            
            # Make request to CanLII case detail API
            detail_url = f"{self.canlii_api_base}/caseBrowse/{database_id}/{case_id}"
            params = {
                "apiKey": self.canlii_api_key
            }
            
            response = requests.get(detail_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract key information
            case_details = {
                "title": data.get("title", ""),
                "citation": data.get("citation", ""),
                "decisionDate": data.get("decisionDate", ""),
                "jurisdiction": data.get("jurisdiction", ""),
                "summary": data.get("summary", ""),
                "url": data.get("url", "")
            }
            
            # Cache the result
            self.case_details_cache[cache_key] = (case_details, datetime.utcnow())
            
            return case_details
            
        except Exception as e:
            print(f"Error fetching case details from CanLII: {str(e)}")
            # Return mock data as fallback
            return {
                "title": "Sample Case Title",
                "citation": "2020 BCCA 123",
                "decisionDate": "2020-05-15",
                "jurisdiction": "British Columbia",
                "summary": "This is a sample case summary for demonstration purposes."
            }
    
    def analyze_evidence_relevance(self, evidence_text: str, case_type: str) -> Dict:
        """
        Analyze evidence relevance for a specific case type
        """
        # Get relevant keywords for case type
        keywords = []
        for category, terms in self.canadian_law_keywords.items():
            if category in case_type.lower() or category == "constitutional":
                keywords.extend(terms)
        
        # Analyze relevance
        analysis = self.analyze_case_relevance(evidence_text, keywords)
        
        return {
            "ai_relevance_score": analysis["relevance_score"],
            "matching_keywords": analysis["matching_keywords"],
            "analyzed_at": analysis["analysis_date"],
            "confidence": "low"  # Free tier confidence level
        }
    
    def get_legal_advice(self, case_summary: str) -> str:
        """
        Get basic legal advice based on case summary
        Uses rule-based approach for free tier
        """
        advice_templates = {
            "constitutional": "Based on your case summary, this appears to involve constitutional rights. Consider reviewing sections 7-15 of the Charter of Rights and Freedoms.",
            "criminal": "This case involves criminal law. Ensure all evidence was obtained legally and review relevant sections of the Criminal Code.",
            "civil": "This is a civil matter. Document all communications and consider alternative dispute resolution options.",
            "administrative": "Administrative law case. Review the enabling legislation for the tribunal or board involved.",
            "default": "Review relevant Canadian legislation and consider consulting with a qualified lawyer for specific advice."
        }
        
        # Simple keyword matching to determine advice type
        case_lower = case_summary.lower()
        advice_type = "default"
        
        for category in advice_templates.keys():
            if category != "default" and category in case_lower:
                advice_type = category
                break
        
        return advice_templates[advice_type]

# Initialize the service
canadian_law_ai = CanadianLawAIService()