"""
Test all API connections before starting development.

Tests:
1. Gemini API connection
2. Qdrant Cloud connection
3. Create and test Qdrant collection

Exit with code 0 if all pass, 1 if any fail.
"""

import os
import sys
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection."""
    print("\n" + "="*60)
    print("TEST 1: Gemini API Connection")
    print("="*60)
    
    try:
        # Import and configure
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ FAILED: GEMINI_API_KEY not found in .env file")
            print("   Troubleshooting: Check that .env file exists and contains GEMINI_API_KEY")
            return False
        
        print(f"✓ Found API key: {api_key[:10]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✓ Configured Gemini API")
        
        # Use gemini-2.0-flash (free tier friendly)
        model_name = 'gemini-2.0-flash'
        
        # Test with model
        model = genai.GenerativeModel(model_name)
        print(f"✓ Created model instance: {model_name}")
        
        # Send test prompt
        response = model.generate_content("Return only the word OK")
        
        if response and response.text:
            print(f"✓ Received response: {response.text.strip()}")
            print("\n✅ GEMINI API TEST PASSED")
            return True
        else:
            print("❌ FAILED: No response text received")
            return False
            
    except ImportError as e:
        print(f"❌ FAILED: Import error - {e}")
        print("   Troubleshooting: Run 'pip install google-generativeai'")
        return False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        print("   Troubleshooting:")
        print("   - Verify API key is correct")
        print("   - Check internet connection")
        print("   - Ensure API key has proper permissions")
        return False


def test_qdrant_connection():
    """Test Qdrant Cloud connection."""
    print("\n" + "="*60)
    print("TEST 2: Qdrant Cloud Connection")
    print("="*60)
    
    try:
        from qdrant_client import QdrantClient
        
        url = os.getenv('QDRANT_URL')
        api_key = os.getenv('QDRANT_API_KEY')
        
        if not url:
            print("❌ FAILED: QDRANT_URL not found in .env file")
            return False
        if not api_key:
            print("❌ FAILED: QDRANT_API_KEY not found in .env file")
            return False
        
        print(f"✓ Found URL: {url[:50]}...")
        print(f"✓ Found API key: {api_key[:20]}...")
        
        # Create client
        client = QdrantClient(url=url, api_key=api_key)
        print("✓ Created Qdrant client")
        
        # Test connection
        collections = client.get_collections()
        print(f"✓ Connected successfully")
        print(f"  Found {len(collections.collections)} collection(s)")
        
        if collections.collections:
            for col in collections.collections:
                print(f"  - {col.name}")
        
        print("\n✅ QDRANT CONNECTION TEST PASSED")
        return True
        
    except ImportError as e:
        print(f"❌ FAILED: Import error - {e}")
        print("   Troubleshooting: Run 'pip install qdrant-client'")
        return False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        print("   Troubleshooting:")
        print("   - Verify QDRANT_URL format: https://xxx.region.aws.cloud.qdrant.io:6333")
        print("   - Check QDRANT_API_KEY is valid")
        print("   - Ensure firewall allows HTTPS on port 6333")
        print("   - Verify Qdrant cloud instance is running")
        return False


def test_qdrant_collection():
    """Create and test Qdrant collection."""
    print("\n" + "="*60)
    print("TEST 3: Qdrant Collection Operations")
    print("="*60)
    
    collection_name = "connection_test"
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        url = os.getenv('QDRANT_URL')
        api_key = os.getenv('QDRANT_API_KEY')
        
        client = QdrantClient(url=url, api_key=api_key)
        
        # Delete collection if exists (cleanup from previous runs)
        try:
            client.delete_collection(collection_name)
            print(f"✓ Cleaned up existing '{collection_name}' collection")
        except:
            pass
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print(f"✓ Created collection '{collection_name}' (768 dimensions, COSINE)")
        
        # Insert test point
        test_vector = np.random.rand(768).tolist()
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=1,
                    vector=test_vector,
                    payload={"test": "data", "type": "connection_test"}
                )
            ]
        )
        print("✓ Inserted test point with random vector")
        
        # Search for similar vectors
        search_results = client.search(
            collection_name=collection_name,
            query_vector=test_vector,
            limit=1
        )
        
        if search_results and len(search_results) > 0:
            print(f"✓ Search successful - found {len(search_results)} result(s)")
            print(f"  Score: {search_results[0].score:.4f}")
        else:
            print("⚠ Warning: Search returned no results")
        
        # Delete test collection
        client.delete_collection(collection_name)
        print(f"✓ Deleted test collection '{collection_name}'")
        
        print("\n✅ QDRANT COLLECTION TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        print("   Troubleshooting:")
        print("   - Check if you have write permissions on Qdrant")
        print("   - Verify collection creation quota")
        print("   - Ensure vector dimensions match (768)")
        
        # Cleanup on failure
        try:
            client.delete_collection(collection_name)
            print(f"  (Cleaned up test collection)")
        except:
            pass
        
        return False


def main():
    """Run all connection tests."""
    print("\n" + "="*60)
    print("🚀 API CONNECTION TESTS")
    print("="*60)
    print("Testing all external API connections...")
    
    results = []
    
    # Test 1: Gemini
    results.append(("Gemini API", test_gemini_api()))
    
    # Test 2: Qdrant Connection
    results.append(("Qdrant Connection", test_qdrant_connection()))
    
    # Test 3: Qdrant Collection (only if connection passed)
    if results[-1][1]:
        results.append(("Qdrant Collections", test_qdrant_collection()))
    else:
        print("\n⏭️  Skipping Qdrant collection test (connection failed)")
        results.append(("Qdrant Collections", False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Ready to start development.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please fix issues before continuing.")
        print("\nQuick fixes:")
        print("  - Verify all API keys in .env file")
        print("  - Check internet connection")
        print("  - Install dependencies: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
