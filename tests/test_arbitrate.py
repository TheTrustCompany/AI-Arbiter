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
        "name": "Data Security and Access Control Policy",
        "description": "Policy agreed upon by both IT management and security team: All employee access to sensitive customer data must be logged and monitored. Any access to customer payment information requires explicit written approval from the Data Protection Officer (DPO) before access is granted. All access logs must be reviewed weekly by the security team. No exceptions are permitted without formal risk assessment documentation.",
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
            "Security audit logs from the past month show that 15 employees accessed customer payment data without any written DPO approval. The access occurred on multiple dates: March 3rd, March 10th, March 17th, and March 24th. No approval forms exist in the DPO office records."
        ),
        create_sample_evidence_data(
            policy_id, 
            opposer_id, 
            "Weekly security log reviews have not been conducted for the past 6 weeks. The security team's own meeting minutes confirm they 'have been too busy with other projects to review access logs as required by the policy.'"
        ),
        create_sample_evidence_data(
            policy_id, 
            opposer_id, 
            "IT management has been granting emergency access to customer payment systems without requiring the mandatory DPO approval, claiming 'business urgency' without any formal risk assessment documentation as required by the policy."
        )
    ]
    
    defender_evidences = [
        create_sample_evidence_data(
            policy_id, 
            defender_id, 
            "We have implemented a new automated logging system that captures all data access attempts. The system is working perfectly and all access is being tracked as required."
        ),
        create_sample_evidence_data(
            policy_id, 
            defender_id, 
            "Our team has been very busy with critical system upgrades and maintenance. We prioritize security but sometimes operational needs require flexible interpretation of policies to keep business running smoothly."
        ),
        create_sample_evidence_data(
            policy_id, 
            defender_id, 
            "The DPO approval process can be slow and sometimes delays urgent business needs. We use our best judgment to grant access when needed and follow up with paperwork later. This approach has not caused any actual security breaches."
        )
    ]
    
    return {
        "policy": policy_data,
        "opposer_evidences": opposer_evidences,
        "defender_evidences": defender_evidences,
        "user_query": "I am filing a complaint against IT management (the defender) for systematic violation of our agreed-upon Data Security and Access Control Policy. The policy clearly states that ALL access to customer payment information requires explicit written DPO approval BEFORE access is granted, with NO EXCEPTIONS unless formal risk assessment documentation exists. However, IT management has been regularly granting access without DPO approval, claiming 'business urgency' and 'flexible interpretation' while completely ignoring the mandatory approval process. They admit to 'following up with paperwork later' which directly violates the policy requirement for PRIOR approval. Additionally, they have failed to conduct the mandatory weekly security log reviews for 6 weeks, violating another core requirement. This is not about operational flexibility - this is about deliberate non-compliance with security policy that puts customer data at risk."
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
                "decision_type", "decision", "message", "confidence_score", "reasoning", "created_at"
            ]
            
            for field in required_fields:
                assert field in arbitration_result, f"Missing required field: {field}"
            
            # Validate decision type
            valid_decision_types = [
                "approve_opposer", "reject_opposer", "clearify",
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

def test_streaming_arbitration():
    """Test streaming arbitration request"""
    print("\n🌊 Testing streaming arbitration request...")
    
    request_data = create_arbitration_request()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/arbitrate/stream",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=120,
            stream=True
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Streaming started successfully")
            
            # Read first few chunks to verify streaming works
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    chunk_count += 1
                    chunk_data = line[6:]  # Remove 'data: ' prefix
                    try:
                        parsed_chunk = json.loads(chunk_data)
                        print(f"📦 Chunk {chunk_count}: {parsed_chunk.get('type', 'unknown')}")
                        
                        # Stop after a few chunks to avoid long wait
                        if chunk_count >= 3:
                            break
                    except json.JSONDecodeError:
                        print(f"📦 Chunk {chunk_count}: Raw content (not JSON)")
            
            print(f"✅ Received {chunk_count} chunks successfully")
            return True
        else:
            print(f"❌ Streaming failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Streaming test error: {str(e)}")
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
        ("Streaming Arbitration", test_streaming_arbitration),
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
