from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import logging

from models import db, Investigation, User, OSINTResult

investigation_bp = Blueprint('investigation', __name__)
logger = logging.getLogger(__name__)

@investigation_bp.route('', methods=['GET'])
@jwt_required()
def list_investigations():
    """List investigations for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        search = request.args.get('search')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Investigation.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter(Investigation.status == status)
        
        if priority:
            query = query.filter(Investigation.priority == priority)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Investigation.name.ilike(search_term),
                    Investigation.description.ilike(search_term),
                    Investigation.target.ilike(search_term)
                )
            )
        
        # Apply sorting
        if sort_by == 'name':
            order_column = Investigation.name
        elif sort_by == 'priority':
            order_column = Investigation.priority
        elif sort_by == 'status':
            order_column = Investigation.status
        elif sort_by == 'updated_at':
            order_column = Investigation.updated_at
        else:
            order_column = Investigation.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        investigations = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'investigations': [inv.to_dict() for inv in investigations],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        })
        
    except Exception as e:
        logger.error(f"List investigations error: {e}")
        return jsonify({'error': 'Failed to retrieve investigations', 'details': str(e)}), 500

@investigation_bp.route('', methods=['POST'])
@jwt_required()
def create_investigation():
    """Create a new investigation"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Investigation name is required'}), 400
        
        # Validate optional fields
        description = data.get('description', '').strip()
        target = data.get('target', '').strip()
        priority = data.get('priority', 'medium')
        tags = data.get('tags', [])
        metadata = data.get('metadata', {})
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if priority not in valid_priorities:
            return jsonify({'error': f'Priority must be one of: {valid_priorities}'}), 400
        
        # Create investigation
        investigation = Investigation(
            name=name,
            description=description,
            target=target,
            priority=priority,
            status='active',
            tags=tags,
            metadata=metadata,
            user_id=user_id
        )
        
        db.session.add(investigation)
        db.session.commit()
        
        return jsonify({
            'message': 'Investigation created successfully',
            'investigation': investigation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create investigation error: {e}")
        return jsonify({'error': 'Failed to create investigation', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>', methods=['GET'])
@jwt_required()
def get_investigation(investigation_id):
    """Get specific investigation details"""
    try:
        user_id = get_jwt_identity()
        
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Get investigation details with related data
        investigation_data = investigation.to_dict()
        
        # Add OSINT results summary
        results_query = OSINTResult.query.filter_by(investigation_id=investigation.id)
        
        investigation_data['osint_results'] = {
            'total': results_query.count(),
            'completed': results_query.filter_by(status='completed').count(),
            'pending': results_query.filter_by(status='pending').count(),
            'failed': results_query.filter_by(status='failed').count(),
            'recent': [
                result.to_dict() for result in 
                results_query.order_by(OSINTResult.created_at.desc()).limit(5).all()
            ]
        }
        
        # Add module usage statistics
        module_stats = db.session.query(
            OSINTResult.module_name,
            db.func.count(OSINTResult.id).label('count')
        ).filter_by(investigation_id=investigation.id).group_by(
            OSINTResult.module_name
        ).all()
        
        investigation_data['module_usage'] = {
            stat.module_name: stat.count for stat in module_stats
        }
        
        return jsonify({
            'investigation': investigation_data
        })
        
    except Exception as e:
        logger.error(f"Get investigation error: {e}")
        return jsonify({'error': 'Failed to retrieve investigation', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>', methods=['PUT'])
@jwt_required()
def update_investigation(investigation_id):
    """Update investigation"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Update allowed fields
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Investigation name cannot be empty'}), 400
            investigation.name = name
        
        if 'description' in data:
            investigation.description = data['description'].strip()
        
        if 'target' in data:
            investigation.target = data['target'].strip()
        
        if 'priority' in data:
            priority = data['priority']
            valid_priorities = ['low', 'medium', 'high', 'critical']
            if priority not in valid_priorities:
                return jsonify({'error': f'Priority must be one of: {valid_priorities}'}), 400
            investigation.priority = priority
        
        if 'status' in data:
            status = data['status']
            valid_statuses = ['active', 'completed', 'archived']
            if status not in valid_statuses:
                return jsonify({'error': f'Status must be one of: {valid_statuses}'}), 400
            investigation.status = status
        
        if 'tags' in data:
            investigation.tags = data['tags']
        
        if 'metadata' in data:
            # Merge metadata instead of replacing
            if investigation.metadata:
                investigation.metadata.update(data['metadata'])
            else:
                investigation.metadata = data['metadata']
        
        investigation.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Investigation updated successfully',
            'investigation': investigation.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update investigation error: {e}")
        return jsonify({'error': 'Failed to update investigation', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>', methods=['DELETE'])
@jwt_required()
def delete_investigation(investigation_id):
    """Delete investigation"""
    try:
        user_id = get_jwt_identity()
        
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Store investigation name for response
        investigation_name = investigation.name
        
        # Delete investigation (cascade will handle related records)
        db.session.delete(investigation)
        db.session.commit()
        
        return jsonify({
            'message': f'Investigation "{investigation_name}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete investigation error: {e}")
        return jsonify({'error': 'Failed to delete investigation', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>/archive', methods=['POST'])
@jwt_required()
def archive_investigation(investigation_id):
    """Archive investigation"""
    try:
        user_id = get_jwt_identity()
        
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        investigation.status = 'archived'
        investigation.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Investigation archived successfully',
            'investigation': investigation.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Archive investigation error: {e}")
        return jsonify({'error': 'Failed to archive investigation', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>/results', methods=['GET'])
@jwt_required()
def get_investigation_results(investigation_id):
    """Get OSINT results for investigation"""
    try:
        user_id = get_jwt_identity()
        
        # Verify investigation ownership
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Query parameters
        module_name = request.args.get('module_name')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = OSINTResult.query.filter_by(investigation_id=investigation.id)
        
        if module_name:
            query = query.filter(OSINTResult.module_name == module_name)
        
        if status:
            query = query.filter(OSINTResult.status == status)
        
        # Order by creation date (newest first)
        query = query.order_by(OSINTResult.created_at.desc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'investigation_id': investigation_id,
            'results': [result.to_dict() for result in results],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        })
        
    except Exception as e:
        logger.error(f"Get investigation results error: {e}")
        return jsonify({'error': 'Failed to retrieve results', 'details': str(e)}), 500

@investigation_bp.route('/<investigation_id>/summary', methods=['GET'])
@jwt_required()
def get_investigation_summary(investigation_id):
    """Get investigation summary and statistics"""
    try:
        user_id = get_jwt_identity()
        
        investigation = Investigation.query.filter_by(
            id=investigation_id,
            user_id=user_id
        ).first()
        
        if not investigation:
            return jsonify({'error': 'Investigation not found'}), 404
        
        # Get results statistics
        results_query = OSINTResult.query.filter_by(investigation_id=investigation.id)
        
        total_results = results_query.count()
        completed_results = results_query.filter_by(status='completed').count()
        pending_results = results_query.filter_by(status='pending').count()
        failed_results = results_query.filter_by(status='failed').count()
        
        # Get module breakdown
        module_stats = db.session.query(
            OSINTResult.module_name,
            OSINTResult.status,
            db.func.count(OSINTResult.id).label('count')
        ).filter_by(investigation_id=investigation.id).group_by(
            OSINTResult.module_name,
            OSINTResult.status
        ).all()
        
        module_breakdown = {}
        for stat in module_stats:
            if stat.module_name not in module_breakdown:
                module_breakdown[stat.module_name] = {}
            module_breakdown[stat.module_name][stat.status] = stat.count
        
        # Get recent activity
        recent_results = results_query.order_by(
            OSINTResult.created_at.desc()
        ).limit(10).all()
        
        # Calculate success rate
        success_rate = (completed_results / total_results * 100) if total_results > 0 else 0
        
        return jsonify({
            'investigation': investigation.to_dict(),
            'statistics': {
                'total_operations': total_results,
                'completed_operations': completed_results,
                'pending_operations': pending_results,
                'failed_operations': failed_results,
                'success_rate': round(success_rate, 2)
            },
            'module_breakdown': module_breakdown,
            'recent_activity': [result.to_dict() for result in recent_results],
            'timeline': {
                'created': investigation.created_at.isoformat(),
                'last_updated': investigation.updated_at.isoformat(),
                'last_activity': recent_results[0].created_at.isoformat() if recent_results else None
            }
        })
        
    except Exception as e:
        logger.error(f"Get investigation summary error: {e}")
        return jsonify({'error': 'Failed to retrieve summary', 'details': str(e)}), 500

@investigation_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_user_investigation_statistics():
    """Get investigation statistics for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get basic counts
        total_investigations = Investigation.query.filter_by(user_id=user_id).count()
        active_investigations = Investigation.query.filter_by(
            user_id=user_id, status='active'
        ).count()
        completed_investigations = Investigation.query.filter_by(
            user_id=user_id, status='completed'
        ).count()
        archived_investigations = Investigation.query.filter_by(
            user_id=user_id, status='archived'
        ).count()
        
        # Get priority breakdown
        priority_stats = db.session.query(
            Investigation.priority,
            db.func.count(Investigation.id).label('count')
        ).filter_by(user_id=user_id).group_by(Investigation.priority).all()
        
        priority_breakdown = {stat.priority: stat.count for stat in priority_stats}
        
        # Get total OSINT operations across all investigations
        total_operations = db.session.query(
            db.func.count(OSINTResult.id)
        ).join(Investigation).filter(Investigation.user_id == user_id).scalar()
        
        return jsonify({
            'total_investigations': total_investigations,
            'active_investigations': active_investigations,
            'completed_investigations': completed_investigations,
            'archived_investigations': archived_investigations,
            'priority_breakdown': priority_breakdown,
            'total_osint_operations': total_operations,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get investigation statistics error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics', 'details': str(e)}), 500