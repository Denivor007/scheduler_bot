import datetime

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from utils.weather_api.weather_api import *
from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import choice, choice_сity
from aiogram import types, Bot
import random

from utils.misc.cookie_list import cookie_list
from loader import dp
from utils.db_api.comands import DBCommands
from states.sity_set import SetSity
from handlers.users.sity_seter import set_city1, set_city2

db = DBCommands()


@dp.message_handler(Command('start'))
async def start(message: Message):
    this_user = types.User.get_current()
    user = await db.get_user(this_user.id)
    text = f"Привіт, {this_user.first_name}!\n\n"
    start = datetime.datetime.now()
    end = datetime.datetime.max
    tasks = await db.get_tasks(start, end)

    if not tasks:
        text += f"<i>Поки-що у вас немає жодних задач </i>\n\n"
    else:
        task = tasks[0]
        text += f"Найближча задача призначена на <b>{task.get_datetime_str()}</b>\n" \
                f"Заплановано:\n" \
                f"<b>{task.name} - </b> {task.description[:100]+('...' if len(task.description) > 100 else '')}\n\n"


    copy_choice = choice
    if not user:
        user = await db.add_new_user()
        text += f"<i>Погода для вас недоступна, введіть команду '\\set_city'</i>\n"
        copy_choice = choice_сity

    elif not user[0].city:
        text += f"<i>Погода для вас недоступна( введіть команду '\\set_city'</i>\n"
        copy_choice = choice_сity

    else:
        text += get_weather(user[0].city)

    text += f"\n🥠 {random.choice(cookie_list)}"
    await message.answer(text=text, reply_markup=copy_choice)


@dp.message_handler(Command('cancel'), state = "*")
@dp.callback_query_handler(text_contains="cancel", state = "*")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.reset_state()
    await start(call.message)


@dp.message_handler(Command('set_morning'))
async def set_morning(message: Message):
    morning = message.text[12:]
    morning = morning.replace(" ", "")
    h, m = morning.split(':')[0], morning.split(':')[1]
    morning = datetime.time(hour=int(h), minute=int(m))
    user = types.User.get_current()
    await db.set_morning(user.id, morning)
    await message.answer(text=f"Ваш \"ранок\" перенесено на {morning}")
    await start(message)


@dp.message_handler()
async def echo(message: Message):
    await db.add_new_user()
