"""
Test script for authentication and email functionality
Run this after setting up your .env file to verify everything works
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.email import send_email, send_welcome_email
from app.core.security import get_password_hash, verify_password, create_access_token

async def test_email():
    """Test email sending functionality"""
    print("\n=== Testing Email Functionality ===")
    
    # Check if SMTP credentials are configured
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        print("❌ SMTP credentials not configured in .env file")
        print("Please set SMTP_USER and SMTP_PASSWORD")
        return False
    
    print(f"✓ SMTP User: {smtp_user}")
    
    # Test sending a simple email
    test_email = input(f"\nEnter email address to send test email (or press Enter to use {smtp_user}): ").strip()
    if not test_email:
        test_email = smtp_user
    
    print(f"\nSending test email to {test_email}...")
    
    try:
        success = await send_email(
            to_email=test_email,
            subject="Test Email from Coffee and AI",
            html_content="""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>🎉 Email Configuration Successful!</h2>
                    <p>Your Coffee and AI application is now configured to send emails.</p>
                    <p>This is a test email to verify your SMTP settings.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">Coffee and AI - Where Intelligence Meets Espresso</p>
                </body>
            </html>
            """,
            text_content="Email Configuration Successful! Your Coffee and AI application can now send emails."
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"Check your inbox at {test_email}")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("\n=== Testing Password Hashing ===")
    
    test_password = "test123"
    print(f"Original password: {test_password}")
    
    # Hash password
    hashed = get_password_hash(test_password)
    print(f"Hashed password: {hashed[:50]}...")
    
    # Verify correct password
    is_valid = verify_password(test_password, hashed)
    print(f"✓ Correct password verification: {is_valid}")
    
    # Verify wrong password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"✓ Wrong password verification: {not is_invalid}")
    
    if is_valid and not is_invalid:
        print("✅ Password hashing works correctly!")
        return True
    else:
        print("❌ Password hashing failed")
        return False

def test_jwt_tokens():
    """Test JWT token creation and validation"""
    print("\n=== Testing JWT Tokens ===")
    
    # Check if SECRET_KEY is configured
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or len(secret_key) < 32:
        print("❌ SECRET_KEY not configured or too short in .env file")
        print("Please set a SECRET_KEY with at least 32 characters")
        return False
    
    print(f"✓ SECRET_KEY configured (length: {len(secret_key)})")
    
    # Create token
    test_data = {"sub": "testuser"}
    token = create_access_token(test_data)
    print(f"✓ Token created: {token[:50]}...")
    
    # Decode token
    from app.core.security import decode_access_token
    username = decode_access_token(token)
    
    if username == "testuser":
        print(f"✓ Token decoded successfully: {username}")
        print("✅ JWT tokens work correctly!")
        return True
    else:
        print("❌ Token decoding failed")
        return False

async def test_welcome_email():
    """Test welcome email template"""
    print("\n=== Testing Welcome Email Template ===")
    
    test_email = input("Enter email address to send welcome email: ").strip()
    if not test_email:
        print("Skipping welcome email test")
        return True
    
    print(f"\nSending welcome email to {test_email}...")
    
    try:
        success = await send_welcome_email(test_email, "TestUser")
        
        if success:
            print("✅ Welcome email sent successfully!")
            print(f"Check your inbox at {test_email}")
            return True
        else:
            print("❌ Failed to send welcome email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")
        return False

def print_configuration_summary():
    """Print current configuration summary"""
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    
    configs = {
        "Database URL": os.getenv("DATABASE_URL", "Not set"),
        "SMTP Host": os.getenv("SMTP_HOST", "Not set"),
        "SMTP Port": os.getenv("SMTP_PORT", "Not set"),
        "SMTP User": os.getenv("SMTP_USER", "Not set"),
        "SMTP Password": "***" if os.getenv("SMTP_PASSWORD") else "Not set",
        "Secret Key": "***" if os.getenv("SECRET_KEY") else "Not set",
        "Token Expiry": f"{os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')} minutes",
    }
    
    for key, value in configs.items():
        status = "✓" if value != "Not set" else "✗"
        print(f"{status} {key}: {value}")
    
    print("="*60 + "\n")

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COFFEE AND AI - AUTHENTICATION & EMAIL TEST SUITE")
    print("="*60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Print configuration
    print_configuration_summary()
    
    # Run tests
    results = {
        "Password Hashing": test_password_hashing(),
        "JWT Tokens": test_jwt_tokens(),
        "Email Sending": await test_email(),
    }
    
    # Optional: Test welcome email
    if results["Email Sending"]:
        test_welcome = input("\nDo you want to test the welcome email template? (y/n): ").strip().lower()
        if test_welcome == 'y':
            results["Welcome Email"] = await test_welcome_email()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("="*60)
    if all_passed:
        print("\n🎉 All tests passed! Your authentication and email system is ready.")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Register a new user via API")
        print("4. Check your email for welcome message")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("\nCommon issues:")
        print("- SMTP credentials not set in .env")
        print("- SECRET_KEY not configured or too short")
        print("- Gmail App Password not generated")
        print("- 2FA not enabled on Gmail account")
    print()

if __name__ == "__main__":
    asyncio.run(main())
