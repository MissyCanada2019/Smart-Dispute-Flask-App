"""
Evidence Routes
Handles evidence upload, review, and analysis functionality
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.case import Case
from models.evidence import Evidence
from models import db
from utils.secure_storage import SecureFileManager
from utils.file_upload import process_file, extract_text_content
from utils.merit_scoring import MeritScoringEngine
import os
from datetime import datetime
import json
from utils.notification_system import notification_manager
from models.notification import NotificationType, NotificationPriority

evidence_bp = Blueprint('evidence', __name__, url_prefix='/evidence')

@evidence_bp.route('/upload')
@login_required
def upload_page():
    """Render evidence upload page"""
    case_id = request.args.get('case_id')
    case = None
    
    if case_id:
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            flash('Case not found or access denied', 'error')
            return redirect(url_for('cases.list_cases'))
    
    return render_template('evidence/upload.html', case=case)

@evidence_bp.route('/upload-and-analyze', methods=['POST'])
@login_required
def upload_and_analyze():
    """Handle evidence upload with AI analysis"""
    try:
        # Get form data
        case_id = request.form.get('case_id', type=int)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        evidence_type = request.form.get('evidence_type', 'other')
        source = request.form.get('source', '').strip()
        relevance_notes = request.form.get('relevance_notes', '').strip()
        evidence_date = request.form.get('evidence_date')
        is_confidential = request.form.get('is_confidential') == 'on'
        is_key_evidence = request.form.get('is_key_evidence') == 'on'
        
        # Validate required fields
        if not case_id or not title or not description:
            return jsonify({
                'success': False,
                'error': 'Case ID, title, and description are required'
            }), 400
        
        # Verify user owns the case
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({
                'success': False,
                'error': 'Case not found or access denied'
            }), 404
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400
        
        # Initialize services
        secure_manager = SecureFileManager()
        merit_engine = MeritScoringEngine()
        
        uploaded_evidence = []
        analysis_results = []
        
        # Process each file
        for i, file in enumerate(files):
            if file.filename == '':
                continue
            
            # Create evidence title for multiple files
            file_title = title if len(files) == 1 else f"{title} - File {i+1}"
            
            # Store file securely
            storage_result = secure_manager.store_file_securely(
                file=file,
                case_id=case_id,
                user_id=current_user.id,
                evidence_title=file_title,
                evidence_description=description
            )
            
            if not storage_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': f'Error storing file {file.filename}: {storage_result.get("error")}'
                }), 500
            
            # Get the evidence record
            evidence = Evidence.query.get(storage_result['evidence_id'])
            
            # Update evidence with additional details
            evidence.title = file_title
            evidence.description = description
            evidence.evidence_type = EvidenceType(evidence_type)
            evidence.is_confidential = is_confidential
            evidence.status = EvidenceStatus.PROCESSING
            
            # Add optional fields
            if source:
                evidence.ai_analysis = evidence.ai_analysis or {}
                evidence.ai_analysis['source'] = source
            
            if relevance_notes:
                evidence.ai_analysis = evidence.ai_analysis or {}
                evidence.ai_analysis['user_relevance_notes'] = relevance_notes
            
            if evidence_date:
                try:
                    evidence.ai_analysis = evidence.ai_analysis or {}
                    evidence.ai_analysis['evidence_date'] = evidence_date
                except:
                    pass
            
            db.session.commit()
            
            # Process file content
            try:
                # Extract text content
                file_data = None
                if evidence.file_path and os.path.exists(evidence.file_path):
                    # Retrieve decrypted file for processing
                    temp_file, file_info = secure_manager.retrieve_file_securely(
                        evidence.id, current_user.id
                    )
                    if temp_file:
                        file_data = temp_file.read()
                        temp_file.close()
                
                if file_data:
                    # Extract text content
                    extracted_text = extract_text_content(file_data, evidence.mime_type, evidence.original_filename)
                    evidence.extracted_text = extracted_text
                    
                    # Perform AI analysis
                    if extracted_text:
                        analysis_result = merit_engine.analyze_evidence_content(
                            content=extracted_text,
                            evidence_type=evidence_type,
                            case_context={
                                'case_type': case.case_type,
                                'province': case.province,
                                'title': case.title,
                                'description': case.description
                            }
                        )
                        
                        # Update evidence with analysis results
                        evidence.ai_summary = analysis_result.get('summary', '')
                        evidence.ai_relevance_score = analysis_result.get('relevance_score', 0.0)
                        evidence.ai_analysis = analysis_result.get('detailed_analysis', {})
                        evidence.legal_keywords = analysis_result.get('legal_keywords', [])
                        evidence.identified_dates = analysis_result.get('identified_dates', [])
                        evidence.identified_names = analysis_result.get('identified_names', [])
                        evidence.identified_locations = analysis_result.get('identified_locations', [])
                        
                        # Set relevance level based on score
                        if evidence.ai_relevance_score >= 0.8:
                            evidence.relevance = 'high'
                        elif evidence.ai_relevance_score >= 0.5:
                            evidence.relevance = 'medium'
                        else:
                            evidence.relevance = 'low'
                        
                        analysis_results.append(analysis_result)
                    
                    evidence.status = EvidenceStatus.ANALYZED
                    evidence.analyzed_at = datetime.utcnow()
                else:
                    evidence.status = EvidenceStatus.PROCESSED
                
                evidence.processed_at = datetime.utcnow()
                
            except Exception as e:
                print(f"Error processing evidence {evidence.id}: {str(e)}")
                evidence.status = EvidenceStatus.ERROR
                evidence.ai_analysis = evidence.ai_analysis or {}
                evidence.ai_analysis['processing_error'] = str(e)
            
            db.session.commit()
            uploaded_evidence.append(evidence)
            
            # Create notification for evidence upload completion
            try:
                if evidence.status == EvidenceStatus.ANALYZED:
                    # Create notification for successful analysis
                    notification_manager.create_notification(
                        user_id=current_user.id,
                        case_id=case_id,
                        notification_type=NotificationType.EVIDENCE_UPDATE,
                        title=f"Evidence Analysis Complete: {evidence.title}",
                        message=f"AI analysis completed for '{evidence.title}'. Relevance score: {evidence.ai_relevance_score:.2f}" if evidence.ai_relevance_score else f"AI analysis completed for '{evidence.title}'.",
                        priority=NotificationPriority.HIGH if evidence.ai_relevance_score and evidence.ai_relevance_score >= 0.8 else NotificationPriority.MEDIUM,
                        action_url=url_for('evidence.view_evidence', evidence_id=evidence.id)
                    )
                    
                    # Special notification for high-relevance evidence
                    if evidence.ai_relevance_score and evidence.ai_relevance_score >= 0.8:
                        notification_manager.create_notification(
                            user_id=current_user.id,
                            case_id=case_id,
                            notification_type=NotificationType.EVIDENCE_UPDATE,
                            title="High-Relevance Evidence Detected!",
                            message=f"'{evidence.title}' has been identified as highly relevant evidence (score: {evidence.ai_relevance_score:.2f}). This could significantly impact your case.",
                            priority=NotificationPriority.HIGH,
                            action_url=url_for('evidence.view_evidence', evidence_id=evidence.id)
                        )
                elif evidence.status == EvidenceStatus.ERROR:
                    # Create notification for processing error
                    notification_manager.create_notification(
                        user_id=current_user.id,
                        case_id=case_id,
                        notification_type=NotificationType.EVIDENCE_UPDATE,
                        title=f"Evidence Processing Error: {evidence.title}",
                        message=f"There was an error processing '{evidence.title}'. Please try re-uploading the file or contact support if the issue persists.",
                        priority=NotificationPriority.MEDIUM,
                        action_url=url_for('evidence.review_evidence', case_id=case_id)
                    )
                else:
                    # Create notification for successful upload
                    notification_manager.create_notification(
                        user_id=current_user.id,
                        case_id=case_id,
                        notification_type=NotificationType.EVIDENCE_UPDATE,
                        title=f"Evidence Uploaded: {evidence.title}",
                        message=f"'{evidence.title}' has been successfully uploaded and is being processed.",
                        priority=NotificationPriority.LOW,
                        action_url=url_for('evidence.view_evidence', evidence_id=evidence.id)
                    )
            except Exception as e:
                print(f"Error creating evidence notification: {str(e)}")
        
        # Generate overall assessment
        overall_assessment = None
        recommendations = []
        
        if analysis_results:
            try:
                overall_assessment = merit_engine.generate_evidence_assessment(
                    analysis_results, case.to_dict()
                )
                recommendations = merit_engine.get_evidence_recommendations(
                    analysis_results, case.to_dict()
                )
            except Exception as e:
                print(f"Error generating overall assessment: {str(e)}")
        
        # Prepare response
        evidence_data = []
        for evidence in uploaded_evidence:
            evidence_data.append({
                'id': evidence.id,
                'title': evidence.title,
                'mime_type': evidence.mime_type,
                'relevance_score': evidence.ai_relevance_score or 0.0,
                'ai_summary': evidence.ai_summary,
                'legal_keywords': evidence.legal_keywords or [],
                'identified_dates': evidence.identified_dates or [],
                'status': evidence.status.value if evidence.status else 'unknown'
            })
        
        return jsonify({
            'success': True,
            'evidence': evidence_data,
            'analysis': {
                'overall_assessment': overall_assessment,
                'recommendations': recommendations,
                'total_files': len(uploaded_evidence),
                'processed_files': sum(1 for e in uploaded_evidence if e.status in [EvidenceStatus.PROCESSED, EvidenceStatus.ANALYZED])
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in upload_and_analyze: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred while processing your evidence: {str(e)}'
        }), 500

@evidence_bp.route('/review/<int:case_id>')
@login_required
def review_evidence(case_id):
    """Review evidence for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        flash('Case not found or access denied', 'error')
        return redirect(url_for('cases.list_cases'))
    
    # Get all evidence for the case
    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(
        Evidence.analyzed_at.desc(),
        Evidence.uploaded_at.desc()
    ).all()
    
    # Group evidence by type
    evidence_by_type = {}
    for evidence in evidence_list:
        evidence_type = evidence.evidence_type.value if evidence.evidence_type else 'other'
        if evidence_type not in evidence_by_type:
            evidence_by_type[evidence_type] = []
        evidence_by_type[evidence_type].append(evidence)
    
    # Calculate statistics
    stats = {
        'total_evidence': len(evidence_list),
        'high_relevance': len([e for e in evidence_list if e.ai_relevance_score and e.ai_relevance_score >= 0.8]),
        'medium_relevance': len([e for e in evidence_list if e.ai_relevance_score and 0.5 <= e.ai_relevance_score < 0.8]),
        'low_relevance': len([e for e in evidence_list if e.ai_relevance_score and e.ai_relevance_score < 0.5]),
        'pending_analysis': len([e for e in evidence_list if e.status in [EvidenceStatus.UPLOADED, EvidenceStatus.PROCESSING]]),
        'analyzed': len([e for e in evidence_list if e.status == EvidenceStatus.ANALYZED])
    }
    
    return render_template('evidence/review.html', 
                         case=case, 
                         evidence_by_type=evidence_by_type,
                         evidence_list=evidence_list,
                         stats=stats)

@evidence_bp.route('/view/<int:evidence_id>')
@login_required
def view_evidence(evidence_id):
    """View individual evidence details"""
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Check access - user must own the case
    case = Case.query.filter_by(id=evidence.case_id, user_id=current_user.id).first()
    if not case:
        flash('Access denied', 'error')
        return redirect(url_for('cases.list_cases'))
    
    # Update access statistics
    evidence.update_access_stats()
    
    return render_template('evidence/view.html', evidence=evidence, case=case)

@evidence_bp.route('/api/list/<int:case_id>')
@login_required
def api_list_evidence(case_id):
    """API endpoint to list evidence for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(
        Evidence.analyzed_at.desc(),
        Evidence.uploaded_at.desc()
    ).all()
    
    evidence_data = [evidence.to_dict() for evidence in evidence_list]
    
    return jsonify({
        'case_id': case_id,
        'case_title': case.title,
        'evidence': evidence_data,
        'total_count': len(evidence_data)
    })

@evidence_bp.route('/api/stats/<int:case_id>')
@login_required
def api_evidence_stats(case_id):
    """API endpoint to get evidence statistics for a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Case not found or access denied'}), 404
    
    evidence_list = Evidence.query.filter_by(case_id=case_id).all()
    
    stats = {
        'total_evidence': len(evidence_list),
        'by_type': {},
        'by_relevance': {
            'high': 0,
            'medium': 0,
            'low': 0,
            'unknown': 0
        },
        'by_status': {},
        'average_relevance': 0.0,
        'total_storage_mb': 0.0
    }
    
    # Calculate statistics
    total_relevance = 0
    relevance_count = 0
    total_storage = 0
    
    for evidence in evidence_list:
        # By type
        evidence_type = evidence.evidence_type.value if evidence.evidence_type else 'other'
        stats['by_type'][evidence_type] = stats['by_type'].get(evidence_type, 0) + 1
        
        # By relevance
        if evidence.ai_relevance_score is not None:
            total_relevance += evidence.ai_relevance_score
            relevance_count += 1
            
            if evidence.ai_relevance_score >= 0.8:
                stats['by_relevance']['high'] += 1
            elif evidence.ai_relevance_score >= 0.5:
                stats['by_relevance']['medium'] += 1
            else:
                stats['by_relevance']['low'] += 1
        else:
            stats['by_relevance']['unknown'] += 1
        
        # By status
        status = evidence.status.value if evidence.status else 'unknown'
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Storage
        if evidence.file_size:
            total_storage += evidence.file_size
    
    if relevance_count > 0:
        stats['average_relevance'] = round(total_relevance / relevance_count, 2)
    
    stats['total_storage_mb'] = round(total_storage / (1024 * 1024), 2)
    
    return jsonify(stats)

@evidence_bp.route('/reanalyze/<int:evidence_id>', methods=['POST'])
@login_required
def reanalyze_evidence(evidence_id):
    """Re-run AI analysis on evidence"""
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Check access
    case = Case.query.filter_by(id=evidence.case_id, user_id=current_user.id).first()
    if not case:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Re-run analysis if we have extracted text
        if evidence.extracted_text:
            merit_engine = MeritScoringEngine()
            
            analysis_result = merit_engine.analyze_evidence_content(
                content=evidence.extracted_text,
                evidence_type=evidence.evidence_type.value if evidence.evidence_type else 'other',
                case_context={
                    'case_type': case.case_type,
                    'province': case.province,
                    'title': case.title,
                    'description': case.description
                }
            )
            
            # Update evidence with new analysis
            evidence.ai_summary = analysis_result.get('summary', '')
            evidence.ai_relevance_score = analysis_result.get('relevance_score', 0.0)
            evidence.ai_analysis = analysis_result.get('detailed_analysis', {})
            evidence.legal_keywords = analysis_result.get('legal_keywords', [])
            evidence.identified_dates = analysis_result.get('identified_dates', [])
            evidence.identified_names = analysis_result.get('identified_names', [])
            evidence.identified_locations = analysis_result.get('identified_locations', [])
            
            evidence.analyzed_at = datetime.utcnow()
            evidence.status = EvidenceStatus.ANALYZED
            
            db.session.commit()
            
            # Create notification for re-analysis completion
            try:
                notification_manager.create_notification(
                    user_id=current_user.id,
                    case_id=evidence.case_id,
                    notification_type=NotificationType.EVIDENCE_UPDATE,
                    title=f"Evidence Re-Analysis Complete: {evidence.title}",
                    message=f"Re-analysis completed for '{evidence.title}'. Updated relevance score: {evidence.ai_relevance_score:.2f}" if evidence.ai_relevance_score else f"Re-analysis completed for '{evidence.title}'.",
                    priority=NotificationPriority.MEDIUM,
                    action_url=url_for('evidence.view_evidence', evidence_id=evidence.id)
                )
            except Exception as e:
                print(f"Error creating re-analysis notification: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Evidence re-analyzed successfully',
                'evidence': evidence.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No extracted text available for analysis'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error re-analyzing evidence: {str(e)}'
        }), 500

# Error handlers
@evidence_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied'}), 403

@evidence_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Evidence not found'}), 404

@evidence_bp.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413