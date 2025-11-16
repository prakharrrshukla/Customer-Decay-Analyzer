"""
Health check routes for API status monitoring.
"""

from flask import Blueprint, jsonify
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

health_bp = Blueprint("health", __name__)


def check_gemini_connection() -> dict:
    """
    Check Gemini API connectivity.
    
    Returns:
        Dict with status and message
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "GEMINI_API_KEY not set"
            }
        
        # Configure and test
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # Try to create model (doesn't make API call, just validates config)
        model = genai.GenerativeModel(model_name)
        
        return {
            "status": "connected",
            "message": f"Gemini API configured ({model_name})",
            "model": model_name
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini connection failed: {str(e)}"
        }


def check_qdrant_connection() -> dict:
    """
    Check Qdrant connectivity.
    
    Returns:
        Dict with status and message
    """
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            return {
                "status": "error",
                "message": "QDRANT_URL or QDRANT_API_KEY not set"
            }
        
        # Create client and test connection
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Try to list collections (validates connection)
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        return {
            "status": "connected",
            "message": "Qdrant connected successfully",
            "collections": collection_names,
            "url": qdrant_url.split('@')[-1] if '@' in qdrant_url else qdrant_url
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Qdrant connection failed: {str(e)}"
        }


def check_data_files() -> dict:
    """
    Check if required data files exist.
    
    Returns:
        Dict with status and file info
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    required_files = [
        "customers.csv",
        "behavior_events.csv",
        "churned_customers.csv"
    ]
    
    missing = []
    found = []
    
    for filename in required_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            found.append(filename)
        else:
            missing.append(filename)
    
    if missing:
        return {
            "status": "incomplete",
            "message": f"Missing files: {', '.join(missing)}",
            "found": found,
            "missing": missing
        }
    else:
        return {
            "status": "ready",
            "message": "All data files present",
            "files": found
        }


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        JSON with service status
    """
    import datetime
    
    # Check all services
    gemini_status = check_gemini_connection()
    qdrant_status = check_qdrant_connection()
    data_status = check_data_files()
    
    # Overall health
    all_connected = (
        gemini_status["status"] == "connected" and
        qdrant_status["status"] == "connected" and
        data_status["status"] == "ready"
    )
    
    response = {
        "status": "healthy" if all_connected else "degraded",
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {
            "gemini": gemini_status,
            "qdrant": qdrant_status,
            "data": data_status
        }
    }
    
    # Add version info
    response["version"] = os.getenv("APP_VERSION", "1.0.0")
    
    # HTTP status code
    status_code = 200 if all_connected else 503
    
    return jsonify(response), status_code


@health_bp.route("/ping", methods=["GET"])
def ping():
    """
    Simple ping endpoint.
    
    Returns:
        JSON with pong message
    """
    return jsonify({
        "message": "pong",
        "status": "alive"
    })
