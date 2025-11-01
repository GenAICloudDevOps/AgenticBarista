"""
Test script for Slack notifications
Run this after setting up your SLACK_WEBHOOK_URL in .env file
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.slack import (
    send_slack_notification,
    send_new_user_notification,
    send_new_order_notification,
    send_order_ready_notification,
    send_error_notification
)

async def test_basic_notification():
    """Test basic Slack notification"""
    print("\n=== Testing Basic Notification ===")
    success = await send_slack_notification(
        "Test notification from Coffee and AI! ☕",
        title="Test Message"
    )
    print(f"✅ Basic notification sent: {success}\n" if success else "❌ Failed to send basic notification\n")
    return success

async def test_new_user_notification():
    """Test new user registration notification"""
    print("=== Testing New User Notification ===")
    success = await send_new_user_notification(
        username="testuser",
        email="test@example.com"
    )
    print(f"✅ New user notification sent: {success}\n" if success else "❌ Failed to send new user notification\n")
    return success

async def test_new_order_notification():
    """Test new order notification"""
    print("=== Testing New Order Notification ===")
    success = await send_new_order_notification(
        order_id=12345,
        customer="testuser",
        total=15.50,
        items_count=3
    )
    print(f"✅ New order notification sent: {success}\n" if success else "❌ Failed to send new order notification\n")
    return success

async def test_order_ready_notification():
    """Test order ready notification"""
    print("=== Testing Order Ready Notification ===")
    success = await send_order_ready_notification(
        order_id=12345,
        customer="testuser"
    )
    print(f"✅ Order ready notification sent: {success}\n" if success else "❌ Failed to send order ready notification\n")
    return success

async def test_error_notification():
    """Test error notification"""
    print("=== Testing Error Notification ===")
    success = await send_error_notification(
        error_type="Database Connection",
        error_message="Failed to connect to PostgreSQL"
    )
    print(f"✅ Error notification sent: {success}\n" if success else "❌ Failed to send error notification\n")
    return success

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COFFEE AND AI - SLACK NOTIFICATION TEST SUITE")
    print("="*60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if webhook is configured
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url or webhook_url == "https://hooks.slack.com/services/YOUR/WEBHOOK/URL":
        print("\n❌ SLACK_WEBHOOK_URL not configured in .env file")
        print("Please set your Slack webhook URL in the .env file")
        return
    
    print(f"\n✓ Slack webhook configured")
    print(f"  URL: {webhook_url[:50]}...")
    
    # Run tests
    results = {
        "Basic Notification": await test_basic_notification(),
        "New User Notification": await test_new_user_notification(),
        "New Order Notification": await test_new_order_notification(),
        "Order Ready Notification": await test_order_ready_notification(),
        "Error Notification": await test_error_notification()
    }
    
    # Print summary
    print("="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("="*60)
    if all_passed:
        print("\n🎉 All tests passed! Your Slack notifications are working.")
        print("\nNext steps:")
        print("1. Check your Slack channel for test messages")
        print("2. Notifications will be sent automatically for:")
        print("   - New user registrations")
        print("   - New orders")
        print("   - Orders ready for pickup")
    else:
        print("\n⚠️  Some tests failed. Please check:")
        print("- Slack webhook URL is correct")
        print("- Webhook has permission to post to the channel")
        print("- Network connectivity")
    print()

if __name__ == "__main__":
    asyncio.run(main())
