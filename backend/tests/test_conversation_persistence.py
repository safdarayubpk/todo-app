"""Tests for conversation persistence (Phase 9).

T062: Test multi-message conversation persistence
T063: Test server restart persistence
"""

import os
import sys
import time
import jwt
import requests
import uuid
from dotenv import load_dotenv

# Load environment
load_dotenv()

BACKEND_URL = "http://localhost:8000"
SECRET_KEY = os.getenv("CHATKIT_SECRET_KEY", "")


def create_test_token(user_id: str) -> str:
    """Create a test JWT token for ChatKit (matching context.py format)."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "exp": now + 3600,
        "iat": now,
        "iss": "todoapp-chatkit",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def test_t062_multi_message_persistence():
    """T062: Test multi-message conversation persistence."""
    print("\n" + "=" * 60)
    print("T062: Test multi-message conversation persistence")
    print("=" * 60)

    user_id = f"t062-test-{uuid.uuid4().hex[:8]}"
    token = create_test_token(user_id)

    # Step 1: Get initial history (should be empty)
    print("\n1. Getting initial history (should be empty)...")
    history_response = requests.get(
        f"{BACKEND_URL}/api/chatkit/history",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    if not history_response.ok:
        print(f"   FAIL: History request failed with {history_response.status_code}")
        return False

    initial_history = history_response.json()
    print(f"   Initial messages: {len(initial_history.get('messages', []))}")

    # Step 2: Send first message (creates conversation)
    print("\n2. Sending first message...")
    msg1_response = requests.post(
        f"{BACKEND_URL}/api/chatkit/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hello, I want to test persistence"},
        timeout=120
    )

    if not msg1_response.ok:
        print(f"   FAIL: First message failed with {msg1_response.status_code}")
        return False

    msg1_data = msg1_response.json()
    if not msg1_data.get("success"):
        print(f"   FAIL: First message error: {msg1_data.get('error')}")
        return False
    print(f"   Response: {msg1_data.get('response', '')[:100]}...")

    # Step 3: Send second message
    print("\n3. Sending second message...")
    msg2_response = requests.post(
        f"{BACKEND_URL}/api/chatkit/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Can you remember what I said?"},
        timeout=120
    )

    if not msg2_response.ok:
        print(f"   FAIL: Second message failed")
        return False

    msg2_data = msg2_response.json()
    if not msg2_data.get("success"):
        print(f"   FAIL: Second message error: {msg2_data.get('error')}")
        return False
    print(f"   Response: {msg2_data.get('response', '')[:100]}...")

    # Step 4: Get history and verify messages persisted
    print("\n4. Getting history to verify persistence...")
    final_history = requests.get(
        f"{BACKEND_URL}/api/chatkit/history",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    if not final_history.ok:
        print(f"   FAIL: Final history request failed")
        return False

    history_data = final_history.json()
    messages = history_data.get("messages", [])
    print(f"   Total messages in history: {len(messages)}")

    # Should have at least 4 messages (2 user + 2 assistant)
    if len(messages) >= 4:
        print("   PASS: Messages persisted correctly!")
        for i, msg in enumerate(messages[:6]):
            print(f"     [{i+1}] {msg['role']}: {msg['content'][:50]}...")
        return True
    else:
        print(f"   FAIL: Expected at least 4 messages, got {len(messages)}")
        return False


def test_t063_server_restart_persistence():
    """T063: Test that messages persist across API calls (simulating restart).

    Note: We can't actually restart the server in this test, but we can verify
    that data persists in the database across separate API calls.
    """
    print("\n" + "=" * 60)
    print("T063: Test database persistence")
    print("=" * 60)

    user_id = f"t063-test-{uuid.uuid4().hex[:8]}"
    token = create_test_token(user_id)

    # Step 1: Create a message
    print("\n1. Creating test conversation...")
    create_response = requests.post(
        f"{BACKEND_URL}/api/chatkit/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "This message should persist in the database"},
        timeout=120
    )

    if not create_response.ok:
        print(f"   FAIL: Create message failed")
        return False

    create_data = create_response.json()
    if not create_data.get("success"):
        print(f"   FAIL: Create error: {create_data.get('error')}")
        return False
    print("   Message created successfully")

    # Step 2: Make a fresh request to history endpoint
    # (This simulates what would happen after a server restart)
    print("\n2. Fetching history in fresh request...")

    # Create a fresh token to ensure no session state
    fresh_token = create_test_token(user_id)

    history_response = requests.get(
        f"{BACKEND_URL}/api/chatkit/history",
        headers={"Authorization": f"Bearer {fresh_token}"},
        timeout=30
    )

    if not history_response.ok:
        print(f"   FAIL: History request failed")
        return False

    history_data = history_response.json()
    messages = history_data.get("messages", [])

    # Verify the original message is still there
    found_original = any(
        "persist in the database" in msg.get("content", "").lower()
        for msg in messages
    )

    if found_original and len(messages) >= 2:
        print(f"   PASS: Found {len(messages)} messages in database!")
        print("   Data persists correctly across API calls")
        return True
    else:
        print(f"   FAIL: Original message not found or insufficient messages")
        print(f"   Messages: {messages}")
        return False


def test_conversation_list():
    """Test listing conversations."""
    print("\n" + "=" * 60)
    print("Bonus: Test conversation list endpoint")
    print("=" * 60)

    user_id = f"conv-list-test-{uuid.uuid4().hex[:8]}"
    token = create_test_token(user_id)

    # Create a conversation
    print("\n1. Creating a conversation...")
    create_response = requests.post(
        f"{BACKEND_URL}/api/chatkit/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Test message for conversation list"},
        timeout=120
    )

    if not create_response.ok or not create_response.json().get("success"):
        print("   FAIL: Could not create conversation")
        return False
    print("   Conversation created")

    # List conversations
    print("\n2. Listing conversations...")
    list_response = requests.get(
        f"{BACKEND_URL}/api/chatkit/conversations",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    if not list_response.ok:
        print(f"   FAIL: List request failed with {list_response.status_code}")
        return False

    list_data = list_response.json()
    conversations = list_data.get("conversations", [])

    if len(conversations) >= 1:
        print(f"   PASS: Found {len(conversations)} conversation(s)")
        for conv in conversations[:3]:
            print(f"     - {conv.get('title', 'Untitled')} (ID: {conv.get('id')})")
        return True
    else:
        print("   FAIL: No conversations found")
        return False


def main():
    """Run all conversation persistence tests."""
    print("\n" + "#" * 60)
    print("# Phase 9 Tests - Conversation Persistence")
    print("#" * 60)

    # Check server health
    try:
        health = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
        if not health.ok:
            print("ERROR: Backend server not healthy")
            sys.exit(1)
        print(f"\nBackend server: {health.json()}")
    except requests.exceptions.RequestException:
        print("ERROR: Could not connect to backend server at", BACKEND_URL)
        sys.exit(1)

    results = {}

    # Run tests
    results["T062"] = test_t062_multi_message_persistence()
    results["T063"] = test_t063_server_restart_persistence()
    results["ConvList"] = test_conversation_list()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_id, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_id}: {status}")
        if not passed:
            all_passed = False

    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
