from datetime import datetime, timedelta

import motor.motor_asyncio

from i17obot import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.DATABASE)
db = client.i17obot


async def create_user(user_data, chat_data):
    return await db.users.insert_one(
        {
            "id": user_data["id"],
            "reminder_set": True,
            "telegram_data": dict(user_data),
            "chat_type": chat_data.type,
        }
    )


async def update_user(user_id, **kwargs):
    kwargs["updated_at"] = datetime.utcnow()
    await db.users.update_one({"id": user_id}, {"$set": kwargs})


async def get_user(user_id):
    return (await db.users.find_one({"id": user_id})) or {}


async def toggle_reminder(user_id):
    user = await get_user(user_id)
    reminder = user.get("reminder_set", False)
    await update_user(user_id, reminder_set=(not reminder))
    return not reminder


async def get_users_with_reminder_on():
    return [
        user
        async for user in db.users.find(
            {
                "reminder_set": True,
                "chat_type": "private",
                "project": {"$in": ["python", None]},
            }
        )
    ]


async def get_all_users():
    return [user async for user in db.users.find()]


async def save_translated_string(user, string):
    db.strings.insert_one(
        {"user": user.id, "string": string.asdict(), "created_at": datetime.utcnow(),}
    )


async def bot_stats():
    total_users = await db.users.count_documents({})
    total_strings = await db.strings.count_documents({})

    past_30_days = datetime.utcnow() - timedelta(days=30)
    strings_last_month = await db.strings.count_documents(
        {"created_at": {"$gt": past_30_days}}
    )

    return {
        "total_users": total_users,
        "total_strings": total_strings,
        "total_strings_past_30_days": strings_last_month,
    }
