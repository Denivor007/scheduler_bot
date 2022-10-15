import asyncio
import datetime

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from utils.weather_api.weather_api import *

from utils.misc.task_lists import get_daily_list

from utils.misc.cookie_list import cookie_list
from loader import dp
from utils.db_api.comands import DBCommands
from states.sity_set import SetSity
from handlers.users.sity_seter import set_city1, set_city2

from loader import bot, storage

db = DBCommands()


async def send_message_remind(delay_in_seconds, task):
    await asyncio.sleep(delay_in_seconds)
    remind_for = int(task.remind_for)
    h = remind_for//60
    m = remind_for % 60
    kiko = ""
    if h:
        kiko += f"{h} годин "
    kiko += f"{m} хвилин"
    message = f"❗️через {kiko} у вас заплановано:\n" \
              f"<b>{task.name} - </b> {task.description}\n\n"
    # choiser = InlineKeyboardMarkup(row_width=1)
    # choiser.insert(
    #     InlineKeyboardButton(
    #         text=f"Перенести задачу",
    #         callback_data=f"reschedule:{task.id}"
    #     )
    # )

    await bot.send_message(task.user_id, message
                           # , reply_markup=choiser
                           )


async def send_message_start_task(delay_in_seconds, task):
    remind_for = int(task.remind_for)
    await asyncio.sleep(delay_in_seconds +(remind_for*60))

    kiko = ""
    message = f"❗️Задачу розпочато!:\n" \
              f"<b>{task.name} - </b> {task.description}\n\n"
    # choiser = InlineKeyboardMarkup(row_width=1)
    # choiser.insert(
    #     InlineKeyboardButton(
    #         text=f"Перенести задачу",
    #         callback_data=f"reschedule:{task.id}"
    #     )
    # )

    await bot.send_message(task.user_id, message
                          # , reply_markup=choiser
                           )


async def task_checker(delay_in_minutes: int):
    print("task_checker started")
    while True:
        now = datetime.datetime.now()
        d2 = datetime.timedelta(days = 1, minutes=20)
        task_list = await db.get_tasks_nwu(now, now+d2)
        bufer_time = datetime.timedelta(minutes=delay_in_minutes, seconds=5)
        for task in task_list:
            print(task)
            remind_for = int(task.remind_for)
            gap = datetime.timedelta(minutes=remind_for)
            now = datetime.datetime.now()
            if (now - bufer_time) < (task.datetime - gap - bufer_time) < now:
                delay = ((task.datetime - gap) - now).total_seconds()
                await send_message_remind(delay, task)
                await send_message_start_task(delay, task)

        start = datetime.datetime.min
        end = now - bufer_time
        old_tasks = await db.get_tasks_nwu(start, end)
        for task in old_tasks:
            await db.delete_task(task.id)
        await asyncio.sleep(delay_in_minutes*60)


async def daily_reminder():
    user_list = await db.get_all_users()
    for user in user_list:
        print(user)
        if user.morning == None:
            user.morning = datetime.time(hour=9, minute=00)
        delta = user.morning.second - datetime.datetime.now().time().second      # 9^00 - 10^10 = -70XB
        if (delta > 0):
            await asyncio.sleep(delta)
        message_date= await get_daily_list(user.user_id)
        await bot.send_message(user.user_id, message_date[0], reply_markup=message_date[1])





