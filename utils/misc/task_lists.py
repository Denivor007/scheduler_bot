import datetime

from keyboards.inline.main_menu import cancel_btn
from utils.db_api.comands import DBCommands
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types, Bot

db = DBCommands()


async def get_daily_list(user_id):
    now = datetime.datetime.now()
    end = now + datetime.timedelta(days=1)
    user = (await db.get_user(user_id))[0]
    tasks = await db.get_tasks(now, end, user_id)
    markup = InlineKeyboardMarkup(row_width=1)

    if not tasks:
        text = "Добрий ранок, а на сьогодні задач немає!\n" \
               "Натисни кнопку \"Меню\" щоб глянути коли найближча (за одно і погоду за вікном перевіриш)"
        markup.insert(cancel_btn)
        return text, markup

    text = f"Ваші задачі на 24 години😌\n" \
           f"<i>починаючи від {user.morning}</i>\n\n"
    for task in tasks:
        text += f"<b>{task.get_datetime_str()}</b> - {task.name}:\n" \
                f"{task.description}\n\n"
        markup.insert(
            InlineKeyboardButton(
                text=f"{task.get_datetime_str()} - {task.name}",
                callback_data=f"choose_task:{task.id}"
            )
        )
    markup.insert(cancel_btn)
    return text, markup



