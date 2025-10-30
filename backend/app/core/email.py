import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Coffee and AI")

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """Send an email via Gmail SMTP"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

async def send_welcome_email(user_email: str, username: str) -> bool:
    """Send welcome email to new user"""
    subject = "Welcome to Coffee and AI! ☕"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6B4423 0%, #8B6F47 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #6B4423; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☕ Welcome to Coffee and AI!</h1>
            </div>
            <div class="content">
                <h2>Hello {username}! 👋</h2>
                <p>Thank you for joining Coffee and AI - where intelligence meets espresso!</p>
                
                <p>Your account has been successfully created. You can now:</p>
                <ul>
                    <li>🤖 Chat with our AI-powered barista</li>
                    <li>☕ Browse our menu and place orders</li>
                    <li>📊 Track your order history</li>
                    <li>⭐ Get personalized recommendations</li>
                </ul>
                
                <p>Our AI assistant uses cutting-edge LangChain and LangGraph technology to provide you with the best coffee ordering experience.</p>
                
                <a href="http://localhost:3000" class="button">Start Ordering Now</a>
                
                <p>If you have any questions, feel free to reach out to our support team.</p>
                
                <p>Enjoy your coffee journey!</p>
                <p><strong>The Coffee and AI Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2024 Coffee and AI. All rights reserved.</p>
                <p>Built with LangChain, LangGraph, and Amazon Nova</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Coffee and AI!
    
    Hello {username}!
    
    Thank you for joining Coffee and AI - where intelligence meets espresso!
    
    Your account has been successfully created. You can now:
    - Chat with our AI-powered barista
    - Browse our menu and place orders
    - Track your order history
    - Get personalized recommendations
    
    Visit http://localhost:3000 to start ordering!
    
    Enjoy your coffee journey!
    The Coffee and AI Team
    """
    
    return await send_email(user_email, subject, html_content, text_content)

async def send_order_confirmation_email(
    user_email: str,
    username: str,
    order_id: int,
    items: List[dict],
    total: float
) -> bool:
    """Send order confirmation email"""
    subject = f"Order Confirmation #{order_id} - Coffee and AI ☕"
    
    # Calculate subtotal and tax
    subtotal = total / 1.08  # Remove tax to get subtotal
    tax = total - subtotal
    
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item['name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${item['price']:.2f}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${item['price'] * item['quantity']:.2f}</td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6B4423 0%, #8B6F47 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .order-box {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            .subtotal-row {{ font-size: 14px; }}
            .tax-row {{ font-size: 14px; color: #666; }}
            .total-row {{ font-weight: bold; font-size: 18px; border-top: 2px solid #333; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Order Confirmed!</h1>
                <p>Order #{order_id}</p>
            </div>
            <div class="content">
                <h2>Thank you, {username}!</h2>
                <p>Your order has been confirmed and is being prepared by our AI-powered barista system.</p>
                
                <div class="order-box">
                    <h3>Order Details</h3>
                    <table>
                        <thead>
                            <tr style="background: #f0f0f0;">
                                <th style="padding: 10px; text-align: left;">Item</th>
                                <th style="padding: 10px; text-align: center;">Qty</th>
                                <th style="padding: 10px; text-align: right;">Price</th>
                                <th style="padding: 10px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                            <tr class="subtotal-row">
                                <td colspan="3" style="padding: 10px; text-align: right;">Subtotal:</td>
                                <td style="padding: 10px; text-align: right;">${subtotal:.2f}</td>
                            </tr>
                            <tr class="tax-row">
                                <td colspan="3" style="padding: 10px; text-align: right;">Tax (8%):</td>
                                <td style="padding: 10px; text-align: right;">${tax:.2f}</td>
                            </tr>
                            <tr class="total-row">
                                <td colspan="3" style="padding: 15px; text-align: right;">Total:</td>
                                <td style="padding: 15px; text-align: right;">${total:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <p><strong>⏱️ Estimated preparation time:</strong> 5-10 minutes</p>
                <p><strong>📍 Pickup location:</strong> Main Counter</p>
                
                <p>We'll notify you when your order is ready!</p>
                
                <p>Thank you for choosing Coffee and AI!</p>
            </div>
            <div class="footer">
                <p>© 2024 Coffee and AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    items_text = "\n".join([
        f"  {item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}"
        for item in items
    ])
    
    text_content = f"""
    Order Confirmed! Order #{order_id}
    
    Thank you, {username}!
    
    Your order has been confirmed and is being prepared.
    
    Order Details:
    {items_text}
    
    Subtotal: ${subtotal:.2f}
    Tax (8%): ${tax:.2f}
    Total: ${total:.2f}
    
    Estimated preparation time: 5-10 minutes
    Pickup location: Main Counter
    
    Thank you for choosing Coffee and AI!
    """
    
    return await send_email(user_email, subject, html_content, text_content)

async def send_order_ready_email(
    user_email: str,
    username: str,
    order_id: int
) -> bool:
    """Send order ready notification email"""
    subject = f"Your Order #{order_id} is Ready! ☕"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; text-align: center; }}
            .ready-icon {{ font-size: 60px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Order Ready!</h1>
            </div>
            <div class="content">
                <div class="ready-icon">☕</div>
                <h2>Hi {username}!</h2>
                <p style="font-size: 18px;">Your order <strong>#{order_id}</strong> is ready for pickup!</p>
                
                <p>Please proceed to the main counter to collect your order.</p>
                
                <p style="margin-top: 30px;">Enjoy your coffee! ☕</p>
            </div>
            <div class="footer">
                <p>© 2024 Coffee and AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Order Ready!
    
    Hi {username}!
    
    Your order #{order_id} is ready for pickup!
    
    Please proceed to the main counter to collect your order.
    
    Enjoy your coffee!
    
    Coffee and AI Team
    """
    
    return await send_email(user_email, subject, html_content, text_content)

async def send_admin_notification(
    subject: str,
    message: str,
    admin_emails: List[str]
) -> bool:
    """Send notification to admin users"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1F2937; color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔔 Admin Notification</h2>
            </div>
            <div class="content">
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>{message}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = True
    for admin_email in admin_emails:
        result = await send_email(admin_email, subject, html_content, message)
        if not result:
            success = False
    
    return success
