import asyncio

from loader import bot, storage
from config import admin_id
from aiogram import types, Bot
from services.setting_comands import set_default_commands
from services.task_reminder import task_checker, daily_reminder

from utils.db_api.comands import DBCommands

bd = DBCommands()


async def set_all_default_commands(bot: Bot):
    await set_default_commands(bot)


async def on_shutdown(dp):
    await bot.close()
    await storage.close()


async def on_startup(dp):
    await bot.send_message(admin_id, "<i>log: бот почав роботу /start</i>")
    await set_all_default_commands(bot)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    loop = asyncio.get_event_loop()
    loop.create_task(task_checker(10))
    loop.create_task(daily_reminder())
    executor.start_polling(dp, loop = loop, on_shutdown=on_shutdown, on_startup = on_startup)
