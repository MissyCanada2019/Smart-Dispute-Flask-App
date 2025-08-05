from flask import Blueprint, render_template
from flask_login import login_required
from utils.db import db
from models.legal_journey import LegalJourney
from utils.legal_journey import LegalJourneyGenerator
import json

journey_bp = Blueprint('journey', __name__, url_prefix='/journey')

@journey_bp.route('/case/<int:case_id>')
@login_required
def view_case_journey(case_id):
    """View the legal journey for a specific case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Get or create journey
    journey = LegalJourney.query.filter_by(case_id=case_id).first()
    if not journey:
        generator = LegalJourneyGenerator()
        journey = generator.create_initial_journey(case_id)
    
    journey_data = json.loads(journey.journey_data)
    return render_template('journey/case_journey.html', 
                         case=case, 
                         journey=journey,
                         journey_data=journey_data)