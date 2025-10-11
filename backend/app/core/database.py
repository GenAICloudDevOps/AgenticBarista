from tortoise import Tortoise
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://barista:barista123@localhost:5432/baristadb")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.menu", "app.models.order", "app.models.customer", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
