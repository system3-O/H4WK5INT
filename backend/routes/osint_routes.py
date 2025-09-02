from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import logging

from models import db, OSINTResult, Investigation, User
from modules.peopint import run_people_intel
from modules.domain_intel import run_domain_intel
from utils.tor_proxy import test_tor_connection

osint_bp = Blueprint('osint', __name__)
logger = logging.getLogger(__name__)

@osint_bp.route('/peopint', methods=['POST'])
@jwt_required()
def people_intelligence():
    """People Intelligence endpoint"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        operation = data.get('operation')
        query = data.get('query')
        investigation_id = data.get('investigation_id')
        
        if not operation or not query:
            return jsonify({'error': 'Operation and query are required'}), 400
        
        # Validate investigation if provided
        investigation = None
        if investigation_id:
            investigation = Investigation.query.filter_by(
                id=investigation_id,
                user_id=user_id
            ).first()
            
            if not investigation:
                return jsonify({'error': 'Investigation not found'}), 404
        
        # Create OSINT result record
        osint_result = OSINTResult(
            module_name='peopint',
            operation_type=operation,
            query=query,
            status='pending',
            investigation_id=investigation_id,
            metadata={
                'user_id': user_id,
                'started_at': datetime.now(timezone.utc).isoformat(),
                'parameters': data
            }
        )
        
        if investigation:
            osint_result.investigation_id = investigation.id
        
        db.session.add(osint_result)
        db.session.commit()
        
        try:
            # Run the operation
            results = run_people_intel(
                operation=operation,
                query=query,
                platforms=data.get('platforms'),
                country_code=data.get('country_code'),
                use_tor=data.get('use_tor', True)
            )
            
            # Update result with success
            osint_result.status = 'completed'
            osint_result.results = results
            osint_result.metadata.update({
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'success': True
            })
            
        except Exception as e:
            # Update result with error
            osint_result.status = 'failed'
            osint_result.error_message = str(e)
            osint_result.metadata.update({
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'success': False,
                'error': str(e)
            })
            
            logger.error(f"People intelligence operation failed: {e}")
        
        db.session.commit()
        
        return jsonify({
            'result_id': str(osint_result.id),
            'status': osint_result.status,
            'results': osint_result.results,
            'error': osint_result.error_message
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"People intelligence endpoint error: {e}")
        return jsonify({'error': 'Operation failed', 'details': str(e)}), 500

@osint_bp.route('/domain', methods=['POST'])
@jwt_required()
def domain_intelligence():
    """Domain Intelligence endpoint"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        operation = data.get('operation')
        domain = data.get('domain')
        investigation_id = data.get('investigation_id')
        
        if not operation or not domain:
            return jsonify({'error': 'Operation and domain are required'}), 400
        
        # Validate investigation if provided
        investigation = None
        if investigation_id:
            investigation = Investigation.query.filter_by(
                id=investigation_id,
                user_id=user_id
            ).first()
            
            if not investigation:
                return jsonify({'error': 'Investigation not found'}), 404
        
        # Create OSINT result record
        osint_result = OSINTResult(
            module_name='domain_intel',
            operation_type=operation,
            query=domain,
            status='pending',
            investigation_id=investigation_id,
            metadata={
                'user_id': user_id,
                'started_at': datetime.now(timezone.utc).isoformat(),
                'parameters': data
            }
        )
        
        if investigation:
            osint_result.investigation_id = investigation.id
        
        db.session.add(osint_result)
        db.session.commit()
        
        try:
            # Run the operation
            results = run_domain_intel(
                operation=operation,
                domain=domain,
                wordlist=data.get('wordlist'),
                ports=data.get('ports'),
                port=data.get('port', 443),
                use_tor=data.get('use_tor', True)
            )
            
            # Update result with success
            osint_result.status = 'completed'
            osint_result.results = results
            osint_result.metadata.update({
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'success': True
            })
            
        except Exception as e:
            # Update result with error
            osint_result.status = 'failed'
            osint_result.error_message = str(e)
            osint_result.metadata.update({
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'success': False,
                'error': str(e)
            })
            
            logger.error(f"Domain intelligence operation failed: {e}")
        
        db.session.commit()
        
        return jsonify({
            'result_id': str(osint_result.id),
            'status': osint_result.status,
            'results': osint_result.results,
            'error': osint_result.error_message
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Domain intelligence endpoint error: {e}")
        return jsonify({'error': 'Operation failed', 'details': str(e)}), 500

@osint_bp.route('/imint', methods=['POST'])
@jwt_required()
def image_intelligence():
    """Image Intelligence endpoint - placeholder"""
    return jsonify({
        'error': 'Image Intelligence module not yet implemented',
        'status': 'coming_soon',
        'available_operations': [
            'reverse_image_search',
            'exif_extraction',
            'metadata_analysis',
            'facial_recognition'
        ]
    }), 501

@osint_bp.route('/socmint', methods=['POST'])
@jwt_required()
def social_media_intelligence():
    """Social Media Intelligence endpoint - placeholder"""
    return jsonify({
        'error': 'Social Media Intelligence module not yet implemented',
        'status': 'coming_soon',
        'available_operations': [
            'profile_search',
            'post_analysis',
            'sentiment_analysis',
            'social_graph_mapping'
        ]
    }), 501

@osint_bp.route('/geoint', methods=['POST'])
@jwt_required()
def geographic_intelligence():
    """Geographic Intelligence endpoint - placeholder"""
    return jsonify({
        'error': 'Geographic Intelligence module not yet implemented',
        'status': 'coming_soon',
        'available_operations': [
            'ip_geolocation',
            'location_search',
            'geographic_correlation',
            'osint_mapping'
        ]
    }), 501

@osint_bp.route('/search', methods=['POST'])
@jwt_required()
def search_intelligence():
    """Search Intelligence endpoint - placeholder"""
    return jsonify({
        'error': 'Search Intelligence module not yet implemented',
        'status': 'coming_soon',
        'available_operations': [
            'google_dorking',
            'advanced_searches',
            'multiple_engines',
            'search_monitoring'
        ]
    }), 501

@osint_bp.route('/results/<result_id>', methods=['GET'])
@jwt_required()
def get_osint_result(result_id):
    """Get specific OSINT result"""
    try:
        user_id = get_jwt_identity()
        
        # Find result - ensure user owns it through investigation
        result = OSINTResult.query.join(Investigation).filter(
            OSINTResult.id == result_id,
            Investigation.user_id == user_id
        ).first()
        
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        
        return jsonify({
            'result': result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Get OSINT result error: {e}")
        return jsonify({'error': 'Failed to retrieve result', 'details': str(e)}), 500

@osint_bp.route('/results', methods=['GET'])
@jwt_required()
def list_osint_results():
    """List OSINT results for user"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        investigation_id = request.args.get('investigation_id')
        module_name = request.args.get('module_name')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = OSINTResult.query.join(Investigation).filter(
            Investigation.user_id == user_id
        )
        
        if investigation_id:
            query = query.filter(OSINTResult.investigation_id == investigation_id)
        
        if module_name:
            query = query.filter(OSINTResult.module_name == module_name)
        
        if status:
            query = query.filter(OSINTResult.status == status)
        
        # Order by creation date (newest first)
        query = query.order_by(OSINTResult.created_at.desc())
        
        # Paginate
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'results': [result.to_dict() for result in results],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total
            }
        })
        
    except Exception as e:
        logger.error(f"List OSINT results error: {e}")
        return jsonify({'error': 'Failed to retrieve results', 'details': str(e)}), 500

@osint_bp.route('/modules', methods=['GET'])
@jwt_required()
def list_osint_modules():
    """List available OSINT modules and their operations"""
    try:
        modules = {
            'peopint': {
                'name': 'People Intelligence',
                'description': 'Intelligence gathering about people and identities',
                'operations': [
                    {
                        'name': 'username_enumeration',
                        'description': 'Check username availability across platforms',
                        'parameters': {
                            'required': ['query'],
                            'optional': ['platforms']
                        }
                    },
                    {
                        'name': 'email_validation',
                        'description': 'Validate email address and check for breaches',
                        'parameters': {
                            'required': ['query'],
                            'optional': []
                        }
                    },
                    {
                        'name': 'phone_lookup',
                        'description': 'Lookup phone number information',
                        'parameters': {
                            'required': ['query'],
                            'optional': ['country_code']
                        }
                    },
                    {
                        'name': 'social_media_search',
                        'description': 'Search for profiles across social media',
                        'parameters': {
                            'required': ['query'],
                            'optional': ['platforms']
                        }
                    }
                ],
                'status': 'active'
            },
            'domain_intel': {
                'name': 'Domain Intelligence',
                'description': 'Domain and network infrastructure analysis',
                'operations': [
                    {
                        'name': 'whois_lookup',
                        'description': 'Perform WHOIS lookup for domain',
                        'parameters': {
                            'required': ['domain'],
                            'optional': []
                        }
                    },
                    {
                        'name': 'dns_enumeration',
                        'description': 'Enumerate DNS records',
                        'parameters': {
                            'required': ['domain'],
                            'optional': []
                        }
                    },
                    {
                        'name': 'subdomain_discovery',
                        'description': 'Discover subdomains',
                        'parameters': {
                            'required': ['domain'],
                            'optional': ['wordlist']
                        }
                    },
                    {
                        'name': 'ssl_analysis',
                        'description': 'Analyze SSL/TLS configuration',
                        'parameters': {
                            'required': ['domain'],
                            'optional': ['port']
                        }
                    },
                    {
                        'name': 'port_scan',
                        'description': 'Scan for open ports',
                        'parameters': {
                            'required': ['domain'],
                            'optional': ['ports']
                        }
                    },
                    {
                        'name': 'technology_detection',
                        'description': 'Detect web technologies',
                        'parameters': {
                            'required': ['domain'],
                            'optional': []
                        }
                    }
                ],
                'status': 'active'
            },
            'imint': {
                'name': 'Image Intelligence',
                'description': 'Image analysis and reverse image search',
                'operations': [],
                'status': 'coming_soon'
            },
            'socmint': {
                'name': 'Social Media Intelligence',
                'description': 'Social media analysis and monitoring',
                'operations': [],
                'status': 'coming_soon'
            },
            'geoint': {
                'name': 'Geographic Intelligence',
                'description': 'Geographic and location-based intelligence',
                'operations': [],
                'status': 'coming_soon'
            },
            'search': {
                'name': 'Search Intelligence',
                'description': 'Search engine intelligence and dorking',
                'operations': [],
                'status': 'coming_soon'
            }
        }
        
        return jsonify({
            'modules': modules,
            'total_modules': len(modules),
            'active_modules': len([m for m in modules.values() if m['status'] == 'active'])
        })
        
    except Exception as e:
        logger.error(f"List OSINT modules error: {e}")
        return jsonify({'error': 'Failed to retrieve modules', 'details': str(e)}), 500

@osint_bp.route('/tor/status', methods=['GET'])
@jwt_required()
def tor_status():
    """Get Tor proxy status"""
    try:
        status = test_tor_connection()
        return jsonify({
            'tor_status': status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Tor status check error: {e}")
        return jsonify({
            'error': 'Failed to check Tor status',
            'details': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@osint_bp.route('/statistics', methods=['GET'])
@jwt_required()
def osint_statistics():
    """Get OSINT usage statistics for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get statistics from database
        total_results = OSINTResult.query.join(Investigation).filter(
            Investigation.user_id == user_id
        ).count()
        
        completed_results = OSINTResult.query.join(Investigation).filter(
            Investigation.user_id == user_id,
            OSINTResult.status == 'completed'
        ).count()
        
        failed_results = OSINTResult.query.join(Investigation).filter(
            Investigation.user_id == user_id,
            OSINTResult.status == 'failed'
        ).count()
        
        # Module usage statistics
        module_stats = db.session.query(
            OSINTResult.module_name,
            db.func.count(OSINTResult.id).label('count')
        ).join(Investigation).filter(
            Investigation.user_id == user_id
        ).group_by(OSINTResult.module_name).all()
        
        module_usage = {stat.module_name: stat.count for stat in module_stats}
        
        return jsonify({
            'total_operations': total_results,
            'completed_operations': completed_results,
            'failed_operations': failed_results,
            'success_rate': round((completed_results / total_results * 100) if total_results > 0 else 0, 2),
            'module_usage': module_usage,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"OSINT statistics error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics', 'details': str(e)}), 500