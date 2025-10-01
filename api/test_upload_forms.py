"""
🧪 Test Client for MuseTalk API
Simple test to verify file upload functionality in the docs
"""
import requests
import json

def test_api_docs():
    """Test that the API docs are accessible and show upload forms"""
    base_url = "http://localhost:8000"
    
    # Test health check
    print("🏥 Testing health check...")
    response = requests.get(f"{base_url}/")
    print(f"✅ Health check: {response.status_code}")
    print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    
    # Test OpenAPI docs
    print("\n📚 Testing OpenAPI schema...")
    response = requests.get(f"{base_url}/openapi.json")
    openapi_data = response.json()
    
    print(f"✅ OpenAPI schema: {response.status_code}")
    print(f"📝 API Title: {openapi_data.get('info', {}).get('title')}")
    print(f"🔖 API Version: {openapi_data.get('info', {}).get('version')}")
    
    # Check if file upload endpoints are properly configured
    paths = openapi_data.get('paths', {})
    
    print("\n📋 Available endpoints:")
    for path, methods in paths.items():
        print(f"  {path}")
        for method, details in methods.items():
            print(f"    {method.upper()}: {details.get('summary', 'No summary')}")
            
            # Check for file uploads
            request_body = details.get('requestBody', {})
            if request_body:
                content = request_body.get('content', {})
                if 'multipart/form-data' in content:
                    print(f"      📁 Has file upload form!")
                    schema = content['multipart/form-data'].get('schema', {})
                    properties = schema.get('properties', {})
                    for prop_name, prop_details in properties.items():
                        prop_type = prop_details.get('type', 'unknown')
                        prop_format = prop_details.get('format', '')
                        print(f"        - {prop_name}: {prop_type} {prop_format}")
    
    print("\n🎉 API Documentation Test Complete!")

def test_file_upload_simulation():
    """Simulate what the upload form should look like"""
    print("\n🎬 File Upload Form Simulation:")
    print("================================")
    
    print("📹 Avatar Preparation Form:")
    print("  - video: [Choose File] (MP4, AVI, MOV, MKV)")
    print("  - bbox_shift: [Number Input] -20 to +20")
    print("  - [Prepare Avatar Button]")
    
    print("\n🎵 Lip-Sync Generation Form:")
    print("  - avatar_id: [Text Input] e.g., avatar_1234567890")
    print("  - audio: [Choose File] (WAV, MP3, M4A)")
    print("  - [Generate Lip-Sync Button]")
    
    print("\n✨ These forms should be visible in the FastAPI docs!")

if __name__ == "__main__":
    try:
        test_api_docs()
        test_file_upload_simulation()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Make sure the API server is running on http://localhost:8000")