"""
Simple server test to identify issues
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("="*60)
print("STARTING SERVER TEST")
print("="*60)

try:
    print("\n1. Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✓ Environment loaded")
    
    print("\n2. Creating Flask app...")
    from flask import Flask, jsonify
    from flask_cors import CORS
    app = Flask(__name__)
    print("   ✓ Flask app created")
    
    print("\n3. Configuring app...")
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DEBUG'] = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    print("   ✓ App configured")
    
    print("\n4. Creating test route...")
    @app.route('/test', methods=['GET'])
    def test():
        return jsonify({'status': 'ok', 'message': 'Server is working!'}), 200
    
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({'status': 'ok', 'message': 'Customer Decay API'}), 200
    
    print("   ✓ Routes created")
    
    print("\n5. Starting server...")
    print("   Server will start on http://localhost:5000")
    print("   Press CTRL+C to stop")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
