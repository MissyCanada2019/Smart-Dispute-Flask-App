"""
Case Law Search Utility
Provides advanced search functionality for Canadian case law using CanLII
"""

from utils.canadian_law_ai import canadian_law_ai
from typing import List, Dict, Optional
import json

class CaseLawSearch:
    """Advanced case law search functionality"""
    
    def __init__(self):
        self.ai_service = canadian_law_ai
    
    def search_by_keywords(self, keywords: List[str], jurisdiction: str = "ca", limit: int = 10) -> List[Dict]:
        """
        Search case law by keywords
        """
        # Combine keywords into a search query
        query = " ".join(keywords)
        return self.ai_service.get_canadian_case_law(query, jurisdiction, limit)
    
    def search_by_citation(self, citation: str) -> Optional[Dict]:
        """
        Search for a specific case by citation
        """
        # For now, we'll search by the citation as a keyword
        cases = self.ai_service.get_canadian_case_law(citation, "ca", 1)
        if cases:
            return cases[0]
        return None
    
    def search_by_date_range(self, start_date: str, end_date: str, jurisdiction: str = "ca", limit: int = 10) -> List[Dict]:
        """
        Search case law within a date range
        Note: This is a simplified implementation as CanLII API may not directly support date range searches
        """
        # We'll search for cases and then filter by date in our application
        query = f"date:{start_date}..{end_date}"
        return self.ai_service.get_canadian_case_law(query, jurisdiction, limit)
    
    def search_by_court(self, court_name: str, jurisdiction: str = "ca", limit: int = 10) -> List[Dict]:
        """
        Search case law from a specific court
        """
        query = f"court:{court_name}"
        return self.ai_service.get_canadian_case_law(query, jurisdiction, limit)
    
    def get_related_cases(self, case_id: str, database_id: str, limit: int = 5) -> List[Dict]:
        """
        Get cases related to a specific case
        """
        # Get the case details first
        case_details = self.ai_service.get_case_details(database_id, case_id)
        
        if not case_details:
            return []
        
        # Extract key terms from the case title and summary for related search
        title = case_details.get("title", "")
        summary = case_details.get("summary", "")
        
        # Combine title and summary for search
        search_terms = f"{title} {summary}"
        
        # Search for related cases
        return self.ai_service.get_canadian_case_law(search_terms, "ca", limit)
    
    def analyze_case_relevance(self, case_data: Dict, search_query: str) -> Dict:
        """
        Analyze how relevant a case is to a search query
        """
        # Extract text from case data
        case_text = f"{case_data.get('title', '')} {case_data.get('citation', '')}"
        
        # Use the AI service's relevance analysis
        return self.ai_service.analyze_case_relevance(case_text, search_query.split())
    
    def format_search_results(self, cases: List[Dict], search_query: str = "") -> List[Dict]:
        """
        Format search results with relevance scores
        """
        formatted_results = []
        
        for case in cases:
            # Add relevance analysis if search query provided
            relevance_data = {}
            if search_query:
                relevance_data = self.analyze_case_relevance(case, search_query)
            
            formatted_case = {
                "case_id": case.get("caseId", {}).get("en", ""),
                "database_id": case.get("databaseId", ""),
                "title": case.get("title", ""),
                "citation": case.get("citation", ""),
                "decision_date": case.get("date", ""),
                "relevance_score": relevance_data.get("relevance_score", 0) if relevance_data else 0,
                "matching_keywords": relevance_data.get("matching_keywords", []) if relevance_data else []
            }
            
            formatted_results.append(formatted_case)
        
        # Sort by relevance score if we have search query
        if search_query:
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return formatted_results

# Initialize the search service
case_law_search = CaseLawSearch()