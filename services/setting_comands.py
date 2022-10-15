from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand('start', "Запуск роботи бота"),
            BotCommand('cancel', "Відмінити дію"),
            BotCommand('set_city', "Задати місто проживання"),
            BotCommand('set_morning', "(/set_morning 9:00) Задати час надходження щоденних оповіщень "),
            BotCommand('help', "Отримання інструкцій щодо роботи бота"),
        ]
    )