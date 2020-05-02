import motor.motor_asyncio

import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.DATABASE)
db = client.i17obot


async def create_user(telegram_user, chat_type):
    user = await db.users.find_one({"id": telegram_user.id})
    if not user:
        user = await db.users.insert_one(
            {
                "id": telegram_user.id,
                "reminder_set": True,
                "telegram_data": dict(telegram_user),
                "chat_type": chat_type,
            }
        )


async def update_user(user_id, **kwargs):
    await db.users.update_one({"id": user_id}, {"$set": kwargs})


async def get_user(user_id):
    return await db.users.find_one({"id": user_id})


async def toggle_reminder(user_id):
    user = await get_user(user_id)
    reminder = user.get("reminder_set", False)
    await db.users.update_one({"id": user_id}, {"$set": {"reminder_set": not reminder}})
    return not reminder


async def get_users_with_reminder_on():
    return [
        user
        async for user in db.users.find({"reminder_set": True, "chat_type": "private"})
    ]


async def get_all_users():
    return [user async for user in db.users.find()]
