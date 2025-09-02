import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from datetime import datetime, timezone

# Local imports
from config import config
from models import db, User, BlacklistedToken

# Route imports
from routes.auth_routes import auth_bp
from routes.osint_routes import osint_bp
from routes.report_routes import report_bp
from routes.investigation_routes import investigation_bp

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize config
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize rate limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Configure logging
    if not app.debug and not app.testing:
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler(app.config['LOG_FILE']),
                logging.StreamHandler()
            ]
        )
    
    # JWT token blacklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = BlacklistedToken.query.filter_by(jti=jti).first()
        return token is not None
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'The token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token is invalid'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'Request does not contain an access token'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has been revoked',
            'message': 'The token has been revoked'
        }), 401
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred'
        }), 500
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'services': {
                'database': db_status,
                'tor': 'checking...'  # Will be implemented in tor_proxy.py
            }
        })
    
    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': 'H4WK5INT OSINT Platform API',
            'version': '1.0.0',
            'description': 'Comprehensive OSINT tool with anonymized Tor routing',
            'endpoints': {
                'auth': '/api/auth',
                'investigations': '/api/investigations',
                'osint': '/api/osint',
                'reports': '/api/reports',
                'tor': '/api/tor'
            },
            'documentation': '/api/docs'
        })
    
    # User profile endpoint
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """Get current user profile"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'user': user.to_dict(),
            'investigations_count': len(user.investigations),
            'reports_count': len(user.reports)
        })
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(osint_bp, url_prefix='/api/osint')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(investigation_bp, url_prefix='/api/investigations')
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        if not app.debug:
            app.logger.info(f'{request.method} {request.url} - {get_remote_address()}')
    
    @app.after_request
    def log_response_info(response):
        if not app.debug:
            app.logger.info(f'Response: {response.status_code}')
        return response
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@h4wk5int.local',
                first_name='Administrator',
                last_name='User',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin_user.set_password('admin123')  # Change this in production
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('Default admin user created')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )