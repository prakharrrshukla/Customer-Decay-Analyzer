"""
Hackathon Setup Verification Script
Checks if all required files and components are in place.
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, description):
    """Check if file exists and return status."""
    exists = os.path.exists(filepath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    print(f"  {status} {description}")
    return exists

def check_env_vars():
    """Check if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["GEMINI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  {GREEN}✓{RESET} {var} is set")
        else:
            print(f"  {RED}✗{RESET} {var} is missing")
            all_present = False
    
    return all_present

def verify_setup():
    """Run comprehensive setup verification."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Customer Decay Analyzer - Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    base_dir = Path(__file__).parent.parent
    all_good = True
    
    # 1. Core files
    print(f"{YELLOW}1. Core Application Files:{RESET}")
    files = [
        ("app.py", "Flask application"),
        ("requirements.txt", "Python dependencies"),
        (".env", "Environment variables"),
        ("README.md", "Documentation"),
        ("API_DOCS.md", "API documentation"),
        ("RUN_TESTS.md", "Testing guide"),
        ("CONTEXT.md", "Technical context"),
    ]
    
    for filename, desc in files:
        filepath = base_dir / filename
        if not check_file(filepath, desc):
            all_good = False
    
    # 2. Models
    print(f"\n{YELLOW}2. AI/ML Models:{RESET}")
    models = [
        ("models/__init__.py", "Models package"),
        ("models/gemini_analyzer.py", "Gemini AI analyzer"),
        ("models/vector_store.py", "Qdrant vector store"),
        ("models/risk_assessor.py", "Combined risk assessor"),
    ]
    
    for filename, desc in models:
        filepath = base_dir / filename
        if not check_file(filepath, desc):
            all_good = False
    
    # 3. Routes
    print(f"\n{YELLOW}3. API Routes:{RESET}")
    routes = [
        ("routes/__init__.py", "Routes package"),
        ("routes/customer_routes.py", "Customer endpoints"),
        ("routes/analytics.py", "Analytics endpoints"),
        ("routes/health_routes.py", "Health check endpoints"),
    ]
    
    for filename, desc in routes:
        filepath = base_dir / filename
        if not check_file(filepath, desc):
            all_good = False
    
    # 4. Utilities
    print(f"\n{YELLOW}4. Utility Functions:{RESET}")
    utils = [
        ("utils/__init__.py", "Utils package"),
        ("utils/data_helpers.py", "Data helper functions"),
    ]
    
    for filename, desc in utils:
        filepath = base_dir / filename
        if not check_file(filepath, desc):
            all_good = False
    
    # 5. Scripts
    print(f"\n{YELLOW}5. Setup & Data Scripts:{RESET}")
    scripts = [
        ("scripts/generate_sample_data.py", "Sample data generator"),
        ("scripts/test_connections.py", "API connection tester"),
        ("scripts/populate_qdrant.py", "Qdrant population"),
        ("scripts/batch_analyze.py", "Batch analyzer"),
    ]
    
    for filename, desc in scripts:
        filepath = base_dir / filename
        if not check_file(filepath, desc):
            all_good = False
    
    # 6. Tests
    print(f"\n{YELLOW}6. Test Suite:{RESET}")
    if not check_file(base_dir / "tests/test_pipeline.py", "Comprehensive test suite"):
        all_good = False
    
    # 7. Data directory
    print(f"\n{YELLOW}7. Data Directory:{RESET}")
    data_dir = base_dir / "data"
    if os.path.exists(data_dir):
        print(f"  {GREEN}✓{RESET} Data directory exists")
        
        # Check for data files
        data_files = ["customers.csv", "behavior_events.csv", "churned_customers.csv"]
        for filename in data_files:
            filepath = data_dir / filename
            exists = os.path.exists(filepath)
            status = f"{GREEN}✓{RESET}" if exists else f"{YELLOW}⚠{RESET}"
            msg = "exists" if exists else "not generated yet"
            print(f"    {status} {filename} ({msg})")
    else:
        print(f"  {RED}✗{RESET} Data directory missing")
        all_good = False
    
    # 8. Environment variables
    print(f"\n{YELLOW}8. Environment Variables:{RESET}")
    if not check_env_vars():
        all_good = False
    
    # 9. Virtual environment
    print(f"\n{YELLOW}9. Virtual Environment:{RESET}")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"  {GREEN}✓{RESET} Virtual environment is active")
    else:
        print(f"  {YELLOW}⚠{RESET} Virtual environment not detected")
        print(f"    Run: .\\venv\\Scripts\\Activate.ps1")
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    if all_good:
        print(f"{GREEN}✅ All core files present!{RESET}")
        print(f"\n{BLUE}Next Steps:{RESET}")
        print(f"  1. Generate sample data: python scripts/generate_sample_data.py")
        print(f"  2. Test connections: python scripts/test_connections.py")
        print(f"  3. Populate Qdrant: python scripts/populate_qdrant.py")
        print(f"  4. Run tests: python tests/test_pipeline.py")
        print(f"  5. Start server: python app.py")
    else:
        print(f"{RED}❌ Some files are missing!{RESET}")
        print(f"\n{YELLOW}Please ensure all required files are created.{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return all_good

if __name__ == "__main__":
    verify_setup()
