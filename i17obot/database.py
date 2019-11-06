import motor.motor_asyncio
from decouple import config

client = motor.motor_asyncio.AsyncIOMotorClient(config("DATABASE"))
db = client.i17obot


async def create_user(telegram_user):
    user = await db.users.find_one({"id": telegram_user.id})
    if not user:
        user = await db.users.insert_one(
            {"id": telegram_user.id, "telegram_data": dict(telegram_user),}
        )


async def toggle_reminder(id):
    user = await db.users.find_one({"id": id})
    reminder = user.get("reminder_set", False)
    await db.users.update_one({"id": id}, {"$set": {"reminder_set": not reminder}})
    return not reminder


async def get_users_with_reminder_on():
    return [user async for user in db.users.find({"reminder_set": True})]
