# Barista Agentic App

A professional cafe application with AI-powered chatbot using multi-agent architecture, built with FastAPI, Next.js, PostgreSQL, and AWS Bedrock.

## Screenshots

![Screenshot 1](screenshots/1.png)
*Landing page with Modern Design and AI features showcase*

![Screenshot 2](screenshots/2.png)
*Homepage showing AI-curated menu with Chat Interface*

![Screenshot 3](screenshots/3.png)
*Footer section with statistics and chat interface*

![Screenshot 4](screenshots/4.png)
*Chat interface with barista assistant asking "why people love coffee" and AI response*

![Screenshot 5](screenshots/5.png)
*Menu display in chat showing coffee items with prices (Espresso $2.50, Americano $3.00)*

![Screenshot 6](screenshots/6.png)
*Order processing chat showing "order a Mocha and Latte" with cart confirmation (1 Mocha, 1 Latte)*

![Screenshot 7](screenshots/7.png)
*Complete order summary with total and confirmation*

## Features

- **Multi-Agent Architecture**: Specialized agents for menu, orders, and confirmations
- **AI-Powered Chat**: Natural language ordering using AWS Bedrock Nova Lite model
- **Professional UI**: Modern landing page with integrated chatbot
- **Real-time Ordering**: Add items to cart, view totals, and confirm orders
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
   cd baristaapp
   cp .env.example .env
   ```

2. **Configure AWS credentials** in `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```

3. **Run the application**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

1. Visit http://localhost:3000
2. Click the chat button in the bottom right
3. Try these commands:
   - "Show me the menu"
   - "Add a latte to my order"
   - "Show my cart"
   - "Confirm my order"

## Architecture

### Multi-Agent System
- **Menu Agent**: Handles menu queries and recommendations
- **Order Agent**: Manages cart operations and pricing
- **Confirmation Agent**: Processes order confirmations
- **Coordinator Agent**: Routes conversations between agents

### Database Schema
- **menu_items**: Coffee, pastries, and food items
- **customers**: Session-based customer tracking
- **orders**: Order history and status tracking

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

- `POST /api/chat` - Chat with AI assistant
- `GET /api/menu` - Get menu items
- `GET /api/orders/{session_id}` - Get user orders
- `WS /api/ws/{session_id}` - WebSocket chat connection

## Environment Variables

See `.env.example` for required configuration.

## License

MIT License
