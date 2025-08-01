import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import openai
import anthropic
from models.case import CaseType
from models.evidence import Evidence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass

class AIServiceManager:
    """Manages AI service integrations for OpenAI and Anthropic"""
    
    def __init__(self):
        # Initialize API clients
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize clients if API keys are available
        self._initialize_clients()
        
        # Configuration for different AI tasks
        self.model_configs = {
            'openai': {
                'evidence_analysis': 'gpt-4-turbo-preview',
                'merit_scoring': 'gpt-4',
                'form_filling': 'gpt-4',
                'legal_advice': 'gpt-4'
            },
            'anthropic': {
                'evidence_analysis': 'claude-3-sonnet-20240229',
                'merit_scoring': 'claude-3-opus-20240229',
                'form_filling': 'claude-3-sonnet-20240229',
                'legal_advice': 'claude-3-opus-20240229'
            }
        }
        
        # Canadian legal context
        self.canadian_legal_context = {
            'provinces': [
                'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick',
                'Newfoundland and Labrador', 'Nova Scotia', 'Ontario',
                'Prince Edward Island', 'Quebec', 'Saskatchewan',
                'Northwest Territories', 'Nunavut', 'Yukon'
            ],
            'court_types': [
                'Supreme Court of Canada', 'Federal Court', 'Tax Court',
                'Provincial Superior Court', 'Provincial Court',
                'Family Court', 'Small Claims Court', 'Youth Court'
            ],
            'case_types': {
                'child_protection': 'Child Protection Services cases involving custody, care, and safety of children',
                'family_court': 'Family law matters including divorce, separation, custody, and support',
                'parental_rights': 'Cases specifically about parental rights and access to children',
                'tribunal': 'Administrative tribunal proceedings and appeals',
                'other': 'Other legal matters requiring self-representation'
            }
        }

    def _initialize_clients(self):
        """Initialize AI service clients with API keys"""
        try:
            # OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found in environment variables")

            # Anthropic client
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Anthropic client initialized successfully")
            else:
                logger.warning("Anthropic API key not found in environment variables")

        except Exception as e:
            logger.error(f"Error initializing AI clients: {str(e)}")

    def is_service_available(self, service: str) -> bool:
        """Check if an AI service is available"""
        if service == 'openai':
            return self.openai_client is not None
        elif service == 'anthropic':
            return self.anthropic_client is not None
        return False

    def analyze_evidence_with_ai(self, evidence: Evidence, preferred_service: str = 'anthropic') -> Dict[str, Any]:
        """
        Analyze evidence using AI for legal relevance and insights
        
        Args:
            evidence: Evidence object to analyze
            preferred_service: 'openai' or 'anthropic'
            
        Returns:
            Dictionary with analysis results
        """
        try:
            if not evidence.extracted_text:
                return {
                    'success': False,
                    'error': 'No text content available for analysis'
                }

            # Choose available service
            service = preferred_service if self.is_service_available(preferred_service) else None
            if not service:
                # Fallback to any available service
                if self.is_service_available('anthropic'):
                    service = 'anthropic'
                elif self.is_service_available('openai'):
                    service = 'openai'
                else:
                    return {
                        'success': False,
                        'error': 'No AI services available'
                    }

            # Get case context
            case = evidence.case
            case_context = self._build_case_context(case)
            
            # Create analysis prompt
            prompt = self._create_evidence_analysis_prompt(evidence, case_context)
            
            # Perform analysis
            if service == 'anthropic':
                result = self._analyze_with_anthropic(prompt, 'evidence_analysis')
            else:
                result = self._analyze_with_openai(prompt, 'evidence_analysis')
            
            return {
                'success': True,
                'service_used': service,
                'analysis_result': result,
                'analyzed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing evidence {evidence.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_case_merit_score(self, case, evidence_list: List[Evidence], preferred_service: str = 'anthropic') -> Dict[str, Any]:
        """
        Calculate overall case merit score using AI analysis
        
        Args:
            case: Case object
            evidence_list: List of Evidence objects
            preferred_service: 'openai' or 'anthropic'
            
        Returns:
            Dictionary with merit score and analysis
        """
        try:
            # Choose available service
            service = preferred_service if self.is_service_available(preferred_service) else None
            if not service:
                if self.is_service_available('anthropic'):
                    service = 'anthropic'
                elif self.is_service_available('openai'):
                    service = 'openai'
                else:
                    return {
                        'success': False,
                        'error': 'No AI services available'
                    }

            # Build comprehensive case summary
            case_summary = self._build_comprehensive_case_summary(case, evidence_list)
            
            # Create merit scoring prompt
            prompt = self._create_merit_scoring_prompt(case_summary)
            
            # Perform analysis
            if service == 'anthropic':
                result = self._analyze_with_anthropic(prompt, 'merit_scoring')
            else:
                result = self._analyze_with_openai(prompt, 'merit_scoring')
            
            # Parse merit score from result
            merit_data = self._parse_merit_score_response(result)
            
            return {
                'success': True,
                'service_used': service,
                'merit_score': merit_data['score'],
                'strength_factors': merit_data['strengths'],
                'weakness_factors': merit_data['weaknesses'],
                'recommendations': merit_data['recommendations'],
                'confidence_level': merit_data['confidence'],
                'analyzed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating merit score for case {case.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_form_field_suggestions(self, form_fields: List[Dict], case_data: Dict, preferred_service: str = 'openai') -> Dict[str, Any]:
        """
        Generate suggestions for court form fields based on case data
        
        Args:
            form_fields: List of form field definitions
            case_data: Case and evidence data
            preferred_service: 'openai' or 'anthropic'
            
        Returns:
            Dictionary with field suggestions
        """
        try:
            # Choose available service
            service = preferred_service if self.is_service_available(preferred_service) else None
            if not service:
                if self.is_service_available('openai'):
                    service = 'openai'
                elif self.is_service_available('anthropic'):
                    service = 'anthropic'
                else:
                    return {
                        'success': False,
                        'error': 'No AI services available'
                    }

            # Create form filling prompt
            prompt = self._create_form_filling_prompt(form_fields, case_data)
            
            # Generate suggestions
            if service == 'anthropic':
                result = self._analyze_with_anthropic(prompt, 'form_filling')
            else:
                result = self._analyze_with_openai(prompt, 'form_filling')
            
            # Parse suggestions
            suggestions = self._parse_form_suggestions(result)
            
            return {
                'success': True,
                'service_used': service,
                'field_suggestions': suggestions,
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating form suggestions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_with_openai(self, prompt: str, task_type: str) -> str:
        """Analyze using OpenAI GPT"""
        if not self.openai_client:
            raise AIServiceError("OpenAI client not initialized")

        model = self.model_configs['openai'][task_type]
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant specializing in Canadian legal matters and self-representation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    def _analyze_with_anthropic(self, prompt: str, task_type: str) -> str:
        """Analyze using Anthropic Claude"""
        if not self.anthropic_client:
            raise AIServiceError("Anthropic client not initialized")

        model = self.model_configs['anthropic'][task_type]
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.3,
            system="You are a helpful AI assistant specializing in Canadian legal matters and self-representation.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text

    def _build_case_context(self, case) -> Dict[str, Any]:
        """Build context information about a case"""
        return {
            'case_type': case.case_type.value if case.case_type else 'unknown',
            'province': case.province,
            'case_description': case.description,
            'jurisdiction': case.jurisdiction,
            'court_name': case.court_name,
            'incident_date': case.incident_date.isoformat() if case.incident_date else None,
            'filing_deadline': case.filing_deadline.isoformat() if case.filing_deadline else None,
            'case_type_description': self.canadian_legal_context['case_types'].get(
                case.case_type.value if case.case_type else 'other',
                'Legal matter requiring self-representation'
            )
        }

    def _create_evidence_analysis_prompt(self, evidence: Evidence, case_context: Dict[str, Any]) -> str:
        """Create prompt for evidence analysis"""
        return f"""
As an expert in Canadian legal matters, please analyze the following evidence for a {case_context['case_type']} case in {case_context['province']}.

CASE CONTEXT:
- Case Type: {case_context['case_type_description']}
- Province: {case_context['province']}
- Court: {case_context.get('court_name', 'Not specified')}
- Description: {case_context.get('case_description', 'Not provided')}

EVIDENCE TO ANALYZE:
Title: {evidence.title}
Type: {evidence.evidence_type.value if evidence.evidence_type else 'unknown'}
Description: {evidence.description or 'No description provided'}

EXTRACTED CONTENT:
{evidence.extracted_text[:2000]}...

Please provide a comprehensive analysis including:

1. RELEVANCE SCORE (0-10): How relevant is this evidence to the case type?

2. KEY INFORMATION EXTRACTED:
   - Important dates mentioned
   - Names of parties or officials
   - Specific legal issues or claims
   - Financial amounts or obligations
   - Deadlines or time limitations

3. LEGAL SIGNIFICANCE:
   - How this evidence supports or weakens the case
   - What legal principles or rights it relates to
   - Potential challenges or weaknesses

4. RECOMMENDATIONS:
   - How to use this evidence effectively
   - What additional evidence might be needed
   - Any concerns or red flags

5. SUMMARY: A concise summary of the evidence and its importance to the case.

Please format your response as structured JSON that can be easily parsed.
"""

    def _create_merit_scoring_prompt(self, case_summary: Dict[str, Any]) -> str:
        """Create prompt for case merit scoring"""
        return f"""
As an expert in Canadian legal matters, please evaluate the overall merit and strength of this legal case:

CASE SUMMARY:
{json.dumps(case_summary, indent=2)}

Please provide a comprehensive merit assessment including:

1. OVERALL MERIT SCORE (0-100): Based on the strength of the case and available evidence

2. STRENGTH FACTORS:
   - Strong pieces of evidence
   - Clear legal rights or violations
   - Good documentation
   - Favorable legal precedents

3. WEAKNESS FACTORS:
   - Missing evidence or documentation
   - Potential legal challenges
   - Procedural issues
   - Statute of limitations concerns

4. CONFIDENCE LEVEL (1-5): How confident are you in this assessment?

5. STRATEGIC RECOMMENDATIONS:
   - Immediate actions to take
   - Additional evidence to gather
   - Legal arguments to focus on
   - Potential settlement considerations

6. CASE OUTLOOK: Brief assessment of likely outcomes

Please format your response as structured JSON for easy parsing.
"""

    def _create_form_filling_prompt(self, form_fields: List[Dict], case_data: Dict) -> str:
        """Create prompt for form field suggestions"""
        return f"""
As an expert in Canadian court forms and legal procedures, please help fill out the following form fields based on the available case information:

FORM FIELDS TO COMPLETE:
{json.dumps(form_fields, indent=2)}

AVAILABLE CASE DATA:
{json.dumps(case_data, indent=2)}

For each form field, please provide:
1. SUGGESTED VALUE: What should go in this field based on the case data
2. CONFIDENCE LEVEL (1-5): How confident are you in this suggestion
3. SOURCE: Which piece of case data supports this suggestion
4. NOTES: Any important considerations or warnings

If insufficient information is available for a field, indicate "INSUFFICIENT_DATA" and suggest what information is needed.

Please format your response as structured JSON mapping field names to suggestions.
"""

    def _build_comprehensive_case_summary(self, case, evidence_list: List[Evidence]) -> Dict[str, Any]:
        """Build comprehensive case summary for merit scoring"""
        evidence_summaries = []
        for evidence in evidence_list:
            if evidence.ai_analysis:
                evidence_summaries.append({
                    'title': evidence.title,
                    'type': evidence.evidence_type.value if evidence.evidence_type else 'unknown',
                    'relevance_score': evidence.ai_relevance_score or 0,
                    'summary': evidence.ai_summary or 'No summary available',
                    'key_points': evidence.ai_analysis.get('key_information', [])
                })

        return {
            'case_info': self._build_case_context(case),
            'evidence_count': len(evidence_list),
            'evidence_summaries': evidence_summaries,
            'total_evidence_relevance': sum(e.ai_relevance_score or 0 for e in evidence_list),
            'case_age_days': (datetime.utcnow() - case.created_at).days if case.created_at else 0
        }

    def _parse_merit_score_response(self, response: str) -> Dict[str, Any]:
        """Parse merit score response from AI"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                data = json.loads(response)
                return {
                    'score': data.get('overall_merit_score', 50),
                    'strengths': data.get('strength_factors', []),
                    'weaknesses': data.get('weakness_factors', []),
                    'recommendations': data.get('strategic_recommendations', []),
                    'confidence': data.get('confidence_level', 3)
                }
        except json.JSONDecodeError:
            pass

        # Fallback to text parsing
        lines = response.split('\n')
        score = 50  # Default score
        
        for line in lines:
            if 'merit score' in line.lower() or 'overall score' in line.lower():
                # Extract number from line
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = min(100, max(0, int(numbers[0])))
                    break

        return {
            'score': score,
            'strengths': ['AI analysis completed'],
            'weaknesses': ['Detailed analysis unavailable'],
            'recommendations': ['Review case details'],
            'confidence': 3
        }

    def _parse_form_suggestions(self, response: str) -> Dict[str, Any]:
        """Parse form field suggestions from AI response"""
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Fallback - return empty suggestions
        return {}


# Global instance
ai_service_manager = AIServiceManager()


# Convenience functions
def analyze_evidence_ai(evidence: Evidence, preferred_service: str = 'anthropic') -> Dict[str, Any]:
    """Convenience function to analyze evidence with AI"""
    return ai_service_manager.analyze_evidence_with_ai(evidence, preferred_service)


def calculate_case_merit_ai(case, evidence_list: List[Evidence], preferred_service: str = 'anthropic') -> Dict[str, Any]:
    """Convenience function to calculate case merit with AI"""
    return ai_service_manager.calculate_case_merit_score(case, evidence_list, preferred_service)


def suggest_form_fields_ai(form_fields: List[Dict], case_data: Dict, preferred_service: str = 'openai') -> Dict[str, Any]:
    """Convenience function to get form field suggestions"""
    return ai_service_manager.generate_form_field_suggestions(form_fields, case_data, preferred_service)