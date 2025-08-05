from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils.db import db
from models.case import Case
from models import FormTemplate, FormField, FormSubmission  # Fixed import
from utils.form_prefill import FormPrefill
import json
from datetime import datetime

form_bp = Blueprint('forms', __name__)

@form_bp.route('/create', methods=['GET'])
def create_form():
    return render_template('forms/create.html')

@form_bp.route('/list', methods=['GET'])
def list_forms():
    forms = FormTemplate.query.all()
    return render_template('forms/list.html', forms=forms)

@form_bp.route('/prefill/<int:form_id>', methods=['GET'])
def prefill_form(form_id):
    form = FormTemplate.query.get(form_id)
    if not form:
        return jsonify({"error": "Form not found"}), 404
    
    prefill = FormPrefill()
    prefill_data = prefill.get_case_form_data(form.case_id, form.form_type)
    
    return jsonify(prefill_data)

@form_bp.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.json
    # Save submission logic here
    return jsonify({"status": "success", "submission_id": 123})