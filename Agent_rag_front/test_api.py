#!/usr/bin/env python3
"""Test API endpoints"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /api/health ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n=== Testing /api/chat ===")
    try:
        payload = {
            "question": "What is machine learning?",
            "chat_history": []
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload():
    """Test upload endpoint"""
    print("\n=== Testing /api/upload ===")
    try:
        # Create a test file
        test_content = "# Test Document\n\nThis is a test document for upload."
        files = {'file': ('test.md', test_content, 'text/markdown')}
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=files,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_reindex():
    """Test reindex endpoint"""
    print("\n=== Testing /api/reindex ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/reindex",
            json={},
            timeout=60
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing RAG Chatbot API")
    print("=" * 50)
    
    # Wait a moment for servers to be ready
    time.sleep(2)
    
    results = {
        "health": test_health(),
        "chat": test_chat(),
        "upload": test_upload(),
        "reindex": test_reindex(),
    }
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    for endpoint, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {endpoint}")
    
    print("=" * 50)
