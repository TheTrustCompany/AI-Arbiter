#!/usr/bin/env python3
"""
Streaming test script for the /arbitrate/stream endpoint

Usage: python test_arbitrate_stream.py
"""

import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
STREAM_ENDPOINT = f"{API_BASE_URL}/arbitrate/stream"


def create_sample_policy_data() -> Dict[str, Any]:
    """Create sample policy data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "name": "Data Security and Access Control Policy",
        "description": (
            "Policy agreed upon by both IT management and security team: "
            "All employee access to sensitive customer data must be logged and monitored. "
            "Any access to customer payment information requires explicit written approval "
            "from the Data Protection Officer (DPO) before access is granted. "
            "All access logs must be reviewed weekly by the security team. "
            "No exceptions are permitted without formal risk assessment documentation."
        ),
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
            "Security audit logs show that 15 employees accessed customer payment data without DPO approval."
        ),
        create_sample_evidence_data(
            policy_id,
            opposer_id,
            "Weekly security log reviews have not been conducted for 6 weeks."
        ),
    ]

    defender_evidences = [
        create_sample_evidence_data(
            policy_id,
            defender_id,
            "We have implemented a new automated logging system that captures all data access attempts."
        ),
        create_sample_evidence_data(
            policy_id,
            defender_id,
            "Operational needs sometimes require flexible interpretation of policies."
        ),
    ]

    return {
        "policy": policy_data,
        "opposer_evidences": opposer_evidences,
        "defender_evidences": defender_evidences,
        "user_query": "I am filing a complaint against IT management for violations of the Data Security Policy."
    }


def test_api_health() -> bool:
    """Check if API is running"""
    print("🏥 Testing API health...")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print(f"✅ API is healthy: {json.dumps(response.json(), indent=2)}")
            return True
        print(f"❌ API health check failed with status: {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False


def test_streaming_arbitration() -> bool:
    """Test the streaming arbitration endpoint"""
    print("🔄 Testing streaming arbitration...")
    
    try:
        # Create test data
        request_data = create_arbitration_request()
        
        print(f"📝 Sending arbitration request for policy: {request_data['policy']['name']}")
        print(f"📊 Opposer evidences: {len(request_data['opposer_evidences'])}")
        print(f"📊 Defender evidences: {len(request_data['defender_evidences'])}")
        
        # Make streaming request
        response = requests.post(
            STREAM_ENDPOINT,
            json=request_data,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✅ Streaming connection established")
        print("📡 Receiving streaming data:")
        
        # Process streaming response
        chunks_received = 0
        has_completion = False
        
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                # SSE format: "data: {json}"
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    try:
                        data = json.loads(data_str)
                        chunks_received += 1
                        
                        # Print chunk info
                        chunk_type = data.get("type", "unknown")
                        if chunk_type == "complete":
                            print(f"🏁 Stream completed: {data.get('message', 'done')}")
                            has_completion = True
                            break
                        elif chunk_type == "error":
                            print(f"❌ Stream error: {data.get('message', 'unknown error')}")
                            return False
                        else:
                            # This is arbitration data
                            print(f"📦 Chunk {chunks_received}: {chunk_type}")
                            print(f"{chunk_type}: {data}")
                            if "decision" in data:
                                decision = data["decision"]
                                print(f"   Decision: {decision.get('verdict', 'N/A')}")
                                print(f"   Confidence: {decision.get('confidence_score', 'N/A')}")
                            # Show a preview of the content for the first few chunks
                            if chunks_received <= 3:
                                content_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                                print(f"   Preview: {content_preview}")
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Failed to parse JSON: {e}")
                        print(f"Raw data: {data_str}")
        
        print(f"📊 Total chunks received: {chunks_received}")
        
        if chunks_received == 0:
            print("❌ No data chunks received")
            return False
        
        if not has_completion:
            print("⚠️ Stream ended without completion message")
            return False
            
        print("✅ Streaming arbitration completed successfully")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Run streaming test"""
    print("🚀 AI Arbiter Streaming Test")
    print("=" * 50)

    if not test_api_health():
        print("❌ API not available. Start the server first.")
        return

    success = test_streaming_arbitration()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Streaming arbitration test passed!")
    else:
        print("⚠️ Streaming arbitration test failed.")


if __name__ == "__main__":
    main()
