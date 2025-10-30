from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db, close_db
from app.api import chat, menu, orders, auth, admin
from app.models.menu import MenuItem
from app.models.user import User
from app.core.security import get_password_hash
import asyncio

app = FastAPI(title="Barista Agentic App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(menu.router, prefix="/api", tags=["menu"])
app.include_router(orders.router, prefix="/api", tags=["orders"])

@app.on_event("startup")
async def startup_event():
    await init_db()
    await seed_menu_data()
    await seed_admin_user()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

async def seed_menu_data():
    # Check if menu items already exist
    existing_items = await MenuItem.all()
    if existing_items:
        return
    
    # Seed initial menu data
    menu_items = [
        {"name": "Espresso", "description": "Rich, bold shot of espresso", "price": 2.50, "category": "coffee"},
        {"name": "Americano", "description": "Espresso with hot water", "price": 3.00, "category": "coffee"},
        {"name": "Latte", "description": "Espresso with steamed milk and foam", "price": 4.50, "category": "coffee"},
        {"name": "Cappuccino", "description": "Equal parts espresso, steamed milk, and foam", "price": 4.00, "category": "coffee"},
        {"name": "Mocha", "description": "Espresso with chocolate and steamed milk", "price": 5.00, "category": "coffee"},
        {"name": "Croissant", "description": "Buttery, flaky French pastry", "price": 3.50, "category": "pastry"},
        {"name": "Blueberry Muffin", "description": "Fresh baked muffin with blueberries", "price": 3.00, "category": "pastry"},
        {"name": "Avocado Toast", "description": "Toasted bread with fresh avocado", "price": 6.00, "category": "food"},
    ]
    
    for item_data in menu_items:
        await MenuItem.create(**item_data)

async def seed_admin_user():
    # Check if admin user already exists
    admin = await User.get_or_none(username="admin")
    if admin:
        return
    
    # Create default admin user
    await User.create(
        email="admin@coffeeandai.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        is_admin=True,
        is_active=True
    )
    print("Default admin user created: username='admin', password='admin123'")

@app.get("/")
async def root():
    return {"message": "Barista Agentic App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
