import os
import aiohttp
import time
from typing import Optional

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

async def send_slack_notification(
    message: str,
    title: Optional[str] = None,
    color: str = "#6B4423"  # Coffee color
) -> bool:
    """Send notification to Slack"""
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL not configured")
        return False
    
    try:
        payload = {
            "attachments": [{
                "color": color,
                "title": title or "Coffee and AI Notification",
                "text": message,
                "footer": "Coffee and AI",
                "ts": int(time.time())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(SLACK_WEBHOOK_URL, json=payload) as response:
                if response.status == 200:
                    print(f"Slack notification sent: {title}")
                    return True
                else:
                    print(f"Slack notification failed: {response.status}")
                    return False
    except Exception as e:
        print(f"Slack notification error: {e}")
        return False


async def send_slack_rich_notification(
    title: str,
    fields: dict,
    color: str = "#6B4423"
) -> bool:
    """Send rich notification with fields to Slack"""
    if not SLACK_WEBHOOK_URL:
        return False
    
    try:
        # Build fields for Slack
        slack_fields = []
        for key, value in fields.items():
            slack_fields.append({
                "type": "mrkdwn",
                "text": f"*{key}:*\n{value}"
            })
        
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": title}
                },
                {
                    "type": "section",
                    "fields": slack_fields
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(SLACK_WEBHOOK_URL, json=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"Slack rich notification error: {e}")
        return False


async def send_new_user_notification(username: str, email: str) -> bool:
    """Send notification for new user registration"""
    return await send_slack_notification(
        f"🎉 New user registered!\n\n"
        f"*Username:* {username}\n"
        f"*Email:* {email}",
        title="New Registration",
        color="#10B981"  # Green
    )


async def send_new_order_notification(order_id: int, customer: str, total: float, items_count: int) -> bool:
    """Send notification for new order"""
    return await send_slack_notification(
        f"☕ New order placed!\n\n"
        f"*Order ID:* #{order_id}\n"
        f"*Customer:* {customer}\n"
        f"*Total:* ${total:.2f}\n"
        f"*Items:* {items_count}",
        title="New Order",
        color="#F59E0B"  # Amber
    )


async def send_order_ready_notification(order_id: int, customer: str) -> bool:
    """Send notification when order is ready"""
    return await send_slack_notification(
        f"✅ Order ready for pickup!\n\n"
        f"*Order ID:* #{order_id}\n"
        f"*Customer:* {customer}",
        title="Order Ready",
        color="#3B82F6"  # Blue
    )


async def send_error_notification(error_type: str, error_message: str) -> bool:
    """Send notification for system errors"""
    return await send_slack_notification(
        f"⚠️ System error occurred!\n\n"
        f"*Type:* {error_type}\n"
        f"*Message:* {error_message}",
        title="System Error",
        color="#EF4444"  # Red
    )
