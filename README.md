# Barista Agentic App

A professional cafe application with AI-powered chatbot using multi-agent architecture, built with FastAPI, Next.js, PostgreSQL, and AWS Bedrock.

## 🆕 New Features

### 🔐 Authentication System
- ✅ User registration and login with JWT tokens
- ✅ Password hashing with bcrypt for security
- ✅ Protected routes for authenticated users
- ✅ Admin-only endpoints for user management
- ✅ Profile dropdown with user information
- ✅ Order history accessible through user profile

### 📧 Email Notifications
- ✅ Welcome emails on registration with professional HTML templates
- ✅ Order confirmation emails with detailed breakdown (Subtotal, Tax 8%, Total)
- ✅ Order ready notifications
- ✅ Admin bulk email capabilities
- ✅ Gmail SMTP integration with app-specific passwords
- ✅ Automatic email sending when logged-in users place orders

### 📊 Order Management
- ✅ Complete order history for authenticated users
- ✅ Tax calculation (8%) displayed in orders and emails
- ✅ Order status tracking (Pending, Confirmed, Preparing, Ready, Completed)
- ✅ Real-time order updates in user profile


## Screenshots

![Screenshot 1](screenshots/1.png)
*Landing page with Modern Design and AI features showcase*

![Screenshot 2](screenshots/2.png)
*Homepage showing LangChain & LangGraph technology stack*

![Screenshot 3](screenshots/3.png)
*Homepage with Menu, Tech and Contact Details*

![Screenshot 4](screenshots/4.png)
*General question with AI Reasoning: "why people love coffee in 2 lines" - shows thinking process before natural response*

![Screenshot 5](screenshots/5.png)
*Menu display with AI Reasoning - agent explains "I have retrieved the menu from the tool" before showing coffee items*

![Screenshot 6](screenshots/6.png)
*Adding Latte and Americano with AI Reasoning showing successful cart addition confirmation*

![Screenshot 7](screenshots/7.png)
*Order confirmation with AI Reasoning, detailed breakdown: 1x Latte ($4.50), 1x Americano ($3.00), Subtotal, Tax (8%), Total ($8.10), and "ready in 5-7 minutes" message*

![Screenshot 8](screenshots/8.png)
*Complete order confirmation showing full details with subtotal, tax calculation, total, and delivery time estimate*

## Features

- **Multi-Agent Architecture**: Specialized agents for menu, orders, and confirmations
- **AI-Powered Chat**: Natural language ordering using AWS Bedrock Nova Lite model
- **Professional UI**: Modern landing page with integrated chatbot and authentication
- **User Authentication**: Secure JWT-based login/registration with profile management
- **Email Notifications**: Automated emails for registration and order confirmations
- **Real-time Ordering**: Add items to cart, view totals with tax, and confirm orders
- **Order History**: Complete order tracking for authenticated users
- **Database Integration**: PostgreSQL with Tortoise ORM and Aerich migrations

## Tech Stack

- **Backend**: FastAPI, LangChain (prerelease), LangGraph, Tortoise ORM, Aerich
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: PostgreSQL
- **AI**: AWS Bedrock (Nova Lite)
- **Deployment**: Docker Compose

## Quick Start

1. **Clone and setup**:
   ```bash
   cd AgenticBarista
   cp .env.example .env
   ```

2. **Configure credentials** in `.env`:
   ```bash
   # AWS Bedrock
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   
   # Authentication (generate with: openssl rand -hex 32)
   SECRET_KEY=your-secret-key-here-generate-using-openssl-rand-hex-32
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Gmail SMTP (for email notifications)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=Coffee and AI
   ```

3. **Generate a secure SECRET_KEY**:
   ```bash
   openssl rand -hex 32
   ```

4. **Setup Gmail App Password** (for email notifications):
   - Go to Google Account → Security → 2-Step Verification
   - Scroll to "App passwords" and generate one
   - Use this password in `SMTP_PASSWORD`

5. **Test authentication and email** (optional):
   ```bash
   cd backend
   python test_auth_email.py
   ```

6. **Run the application**:
   ```bash
   docker-compose up -d --build
   ```

7. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Default Admin: username=`admin`, password=`admin123`

8. **Register and Login**:
   - Click "Login / Register" button on the landing page
   - Create a new account with your email
   - You'll receive a welcome email
   - Login to access order history and email notifications

## Usage

### For Guest Users
1. Visit http://localhost:3000
2. Click the chat button in the bottom right
3. Try these commands:
   - "Show me the menu"
   - "Add a latte to my order"
   - "Show my cart"
   - "Confirm my order"

### For Registered Users
1. Click "Login / Register" and create an account
2. You'll receive a welcome email
3. Place orders through the AI chatbot
4. Receive order confirmation emails with tax breakdown
5. View your order history by clicking your profile dropdown → "My Orders"
6. See detailed order information including:
   - Order items and quantities
   - Subtotal, Tax (8%), and Total
   - Order status and timestamp

## Architecture

### Multi-Agent System
- **Menu Agent**: Handles menu queries and recommendations
- **Order Agent**: Manages cart operations and pricing
- **Confirmation Agent**: Processes order confirmations
- **Coordinator Agent**: Routes conversations between agents

### Database Schema
- **menu_items**: Coffee, pastries, and food items with prices
- **customers**: Session-based customer tracking (uses email for logged-in users)
- **orders**: Order history with items, totals (including 8% tax), and status tracking
- **users**: User accounts with authentication, email, and admin flags

## Development

### Backend Development
```bash
cd backend
pip install --pre -U langchain
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
cd backend
aerich init -t app.core.database.TORTOISE_ORM
aerich init-db
aerich migrate
aerich upgrade
```

## API Endpoints

### Chat & Menu
- `POST /api/chat` - Chat with AI assistant
- `GET /api/menu` - Get menu items
- `WS /api/ws/{session_id}` - WebSocket chat connection

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (protected)

### Orders
- `GET /api/orders/{session_id}` - Get orders by session
- `GET /api/my-orders` - Get authenticated user's order history (protected)
- `POST /api/order/{order_id}/notify` - Send order confirmation email

### Admin (Protected)
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{user_id}` - Update user
- `DELETE /api/admin/users/{user_id}` - Delete user
- `POST /api/admin/email/bulk` - Send bulk emails

## Environment Variables

See `.env.example` for required configuration.

## License

MIT License
