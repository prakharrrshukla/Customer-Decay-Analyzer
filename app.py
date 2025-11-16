"""
Customer Decay Prediction Backend
Main Flask application entry point
"""
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Enable CORS for frontend integration
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'customer-decay-backend',
        'version': '1.0.0'
    }), 200


# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Customer Decay Prediction API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'customers': '/api/customers',
            'analytics': '/api/analytics',
            'ai': '/api/ai'
        }
    }), 200


# Import and register blueprints (after app creation to avoid circular imports)
def register_blueprints():
    """Register API route blueprints."""
    try:
        from routes.customer_routes import customer_bp
        from routes.analytics import analytics_bp
        from routes.health_routes import health_bp
        
        app.register_blueprint(customer_bp, url_prefix='/api/customers')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(health_bp, url_prefix='/api')
        
        print("✓ All blueprints registered successfully")
    except ImportError as e:
        print(f"⚠ Warning: Could not import some blueprints: {e}")
        print("  Routes will be available once implemented")


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # Register blueprints
    register_blueprints()
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"\n{'='*50}")
    print(f"🚀 Customer Decay Prediction Backend")
    print(f"{'='*50}")
    print(f"   Server: http://{host}:{port}")
    print(f"   Health: http://{host}:{port}/health")
    print(f"   Debug:  {app.config['DEBUG']}")
    print(f"{'='*50}\n")
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )
