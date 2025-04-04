from config import config
from tortoise import Tortoise

db_link = config("db_path")


async def init_db():
    await Tortoise.init(
        db_url=db_link,
        modules={'models': [
            'core.database.models',]
        },
    )
    await Tortoise.generate_schemas()
