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
    """Test streaming arbitration request"""
    print("\n🌊 Testing streaming arbitration request...")

    request_data = create_arbitration_request()

    try:
        response = requests.post(
            STREAM_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=120,
            stream=True
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Streaming failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        print("✅ Streaming started successfully")
        chunk_count = 0

        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                chunk_count += 1
                chunk_data = line[6:]
                try:
                    parsed_chunk = json.loads(chunk_data)
                    print(f"📦 Chunk {chunk_count}: {parsed_chunk.get('type', 'unknown')}")
                    print(f"    Content: {parsed_chunk}")
                except json.JSONDecodeError:
                    print(f"📦 Chunk {chunk_count}: Raw content (not JSON)")

                if chunk_count >= 3:  # Stop early
                    break

        print(f"✅ Received {chunk_count} chunks successfully")
        return True

    except Exception as e:
        print(f"❌ Streaming test error: {e}")
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
