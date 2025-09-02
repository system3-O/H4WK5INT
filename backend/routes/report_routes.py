from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import logging

from models import db, Report, Investigation, User

report_bp = Blueprint('report', __name__)
logger = logging.getLogger(__name__)

@report_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """Generate report for investigation"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        investigation_id = data.get('investigation_id')
        report_type = data.get('report_type', 'pdf')
        name = data.get('name', f'Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        if not investigation_id:
            return jsonify({'error': 'Investigation ID is required'}), 400
        
        # Validate investigation ownership
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Validate report type
        valid_types = ['pdf', 'html', 'json', 'markdown', 'csv']
        if report_type not in valid_types:
            return jsonify({'error': f'Report type must be one of: {valid_types}'}), 400
        
        # Create report record
        report = Report(
            name=name,
            report_type=report_type,
            status='generating',
            parameters=data,
            user_id=user_id,
            investigation_id=investigation_id,
            metadata={
                'started_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        db.session.add(report)
        db.session.commit()
        
        # TODO: Implement actual report generation
        # For now, mark as completed with placeholder
        report.status = 'completed'
        report.file_path = f'/reports/{report.id}.{report_type}'
        report.file_size = 1024  # Placeholder size
        report.metadata.update({
            'completed_at': datetime.now(timezone.utc).isoformat(),
            'note': 'Report generation not yet implemented'
        })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report generation started',
            'report': report.to_dict()
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Report generation error: {e}")
        return jsonify({'error': 'Failed to generate report', 'details': str(e)}), 500

@report_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get report details"""
    try:
        user_id = get_jwt_identity()
        
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify({
            'report': report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Get report error: {e}")
        return jsonify({'error': 'Failed to retrieve report', 'details': str(e)}), 500

@report_bp.route('/<report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """Download report file"""
    try:
        user_id = get_jwt_identity()
        
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        if report.status != 'completed':
            return jsonify({'error': 'Report is not ready for download'}), 400
        
        # TODO: Implement actual file download
        return jsonify({
            'error': 'Report download not yet implemented',
            'report_id': report_id,
            'file_path': report.file_path
        }), 501
        
    except Exception as e:
        logger.error(f"Download report error: {e}")
        return jsonify({'error': 'Failed to download report', 'details': str(e)}), 500

@report_bp.route('', methods=['GET'])
@jwt_required()
def list_reports():
    """List reports for user"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        investigation_id = request.args.get('investigation_id')
        report_type = request.args.get('report_type')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Report.query.filter_by(user_id=user_id)
        
        if investigation_id:
            query = query.filter(Report.investigation_id == investigation_id)
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        if status:
            query = query.filter(Report.status == status)
        
        # Order by creation date (newest first)
        query = query.order_by(Report.created_at.desc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        reports = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        })
        
    except Exception as e:
        logger.error(f"List reports error: {e}")
        return jsonify({'error': 'Failed to retrieve reports', 'details': str(e)}), 500

@report_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete report"""
    try:
        user_id = get_jwt_identity()
        
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # TODO: Delete actual file from filesystem
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete report error: {e}")
        return jsonify({'error': 'Failed to delete report', 'details': str(e)}), 500