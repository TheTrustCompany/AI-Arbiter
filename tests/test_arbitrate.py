#!/usr/bin/env python3
"""
Simple test script for the /arbitrate endpoint

This is a standalone test script that can be run without additional dependencies.
Usage: python test_arbitrate_simple.py
"""

import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
ARBITRATE_ENDPOINT = f"{API_BASE_URL}/arbitrate"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

def create_sample_policy_data() -> Dict[str, Any]:
    """Create sample policy data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "name": "Remote Work Policy",
        "description": "Policy agreed upon by both management and employees: Employees are allowed to work remotely up to 3 days per week, but must maintain productivity standards and attend all mandatory meetings in person.",
        "created_at": datetime.utcnow().isoformat()
    }

def create_sample_evidence_data(policy_id: str, submitter_id: str, content: str) -> Dict[str, Any]:
    """Create sample evidence data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "policy_id": policy_id,
        "submitter_id": submitter_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }

def create_arbitration_request() -> Dict[str, Any]:
    """Create a complete arbitration request"""
    policy_data = create_sample_policy_data()
    policy_id = policy_data["id"]
    
    opposer_id = str(uuid.uuid4())
    defender_id = policy_data["creator_id"]
    
    opposer_evidences = [
        create_sample_evidence_data(
            policy_id, 
            opposer_id, 
            "Management has failed to enforce the productivity standards outlined in the remote work policy. Employee productivity has dropped 20% with no corrective action taken."
        ),
        create_sample_evidence_data(
            policy_id, 
            opposer_id, 
            "The policy requires attendance at mandatory meetings, but management has been allowing remote workers to skip these meetings without consequences."
        )
    ]
    
    defender_evidences = [
        create_sample_evidence_data(
            policy_id, 
            defender_id, 
            "We have implemented new productivity tracking tools and are working on improvement plans for underperforming remote workers. The policy is being followed."
        ),
        create_sample_evidence_data(
            policy_id, 
            defender_id, 
            "Meeting attendance has improved 15% since we clarified the mandatory meeting requirements. We are enforcing the policy appropriately."
        )
    ]
    
    return {
        "policy": policy_data,
        "opposer_evidences": opposer_evidences,
        "defender_evidences": defender_evidences,
        "user_query": "I am filing a complaint that management (the defender) is not properly enforcing the remote work policy that we all agreed upon. They are not maintaining the productivity standards and meeting attendance requirements as specified in the policy."
    }

def test_api_health():
    """Test if the API is running and healthy"""
    try:
        print("🏥 Testing API health...")
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy: {json.dumps(health_data, indent=2)}")
            return True
        else:
            print(f"❌ API health check failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_valid_arbitration():
    """Test a valid arbitration request"""
    print("\n🧪 Testing valid arbitration request...")
    
    request_data = create_arbitration_request()
    
    try:
        response = requests.post(
            ARBITRATE_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=600
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            # Validate response structure
            assert "status" in response_data, "Missing 'status' in response"
            assert response_data["status"] == "success", f"Expected success, got {response_data['status']}"
            assert "result" in response_data, "Missing 'result' in response"
            
            result = response_data["result"]
            assert "arbitration_result" in result, "Missing 'arbitration_result'"
            assert "metadata" in result, "Missing 'metadata'"
            
            arbitration_result = result["arbitration_result"]
            required_fields = [
                "decision_id", "policy_id", "opposer_id", "defender_id",
                "decision_type", "decision", "confidence_score", "reasoning", "created_at"
            ]
            
            for field in required_fields:
                assert field in arbitration_result, f"Missing required field: {field}"
            
            # Validate decision type
            valid_decision_types = [
                "approve_opposer", "reject_opposer", "needs_more_info",
                "request_opposer_evidence", "request_defender_evidence"
            ]
            decision_type = arbitration_result["decision_type"]
            assert decision_type in valid_decision_types, f"Invalid decision type: {decision_type}"
            
            # Validate confidence score
            confidence = arbitration_result["confidence_score"]
            assert 0.0 <= confidence <= 1.0, f"Confidence score {confidence} not in range [0.0, 1.0]"
            
            print("✅ Valid arbitration test passed!")
            return True
        else:
            print(f"❌ Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in arbitration test: {str(e)}")
        return False

def test_missing_policy():
    """Test arbitration request without policy"""
    print("\n🧪 Testing request without policy...")
    
    request_data = {
        "opposer_evidences": [],
        "defender_evidences": [],
        "user_query": "Test without policy"
    }
    
    try:
        response = requests.post(
            ARBITRATE_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        # Should return error for missing policy
        if response.status_code == 500:
            print("✅ Missing policy test passed (correctly returned error)")
            return True
        else:
            print(f"❌ Expected error status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in missing policy test: {str(e)}")
        return False

def test_minimal_request():
    """Test minimal valid arbitration request"""
    print("\n🧪 Testing minimal valid request...")
    
    policy_data = {
        "id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "name": "Minimal Test Policy"
    }
    
    request_data = {
        "policy": policy_data,
        "opposer_evidences": [],
        "defender_evidences": []
    }
    
    try:
        response = requests.post(
            ARBITRATE_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            assert response_data["status"] == "success"
            print("✅ Minimal request test passed!")
            return True
        else:
            print(f"❌ Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in minimal request test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Arbiter /arbitrate Endpoint Test Suite")
    print("=" * 60)
    print("This script tests the arbitration functionality of the AI Arbiter API.")
    print("Make sure the API server is running before running tests.")
    print()
    
    # Test health first
    if not test_api_health():
        print("\n❌ API is not available. Start the server with: python run.py")
        return
    
    # Run tests
    tests = [
        ("Valid Arbitration", test_valid_arbitration),
        ("Missing Policy", test_missing_policy),
        ("Minimal Request", test_minimal_request),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
