from contextlib import suppress

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from keyboards.inline.callback_datas import date_callback
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command


from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import *

from utils.db_api.comands import DBCommands

from .default import start
from loader import dp
import datetime
from states.task_selection import TaskSelector
from utils.misc.task_datatime import data_checker, to_datatime, split_on_week


db = DBCommands()

dict_of_month = {
    1: "січень",
    2: "лютий",
    3: "березень",
    4: "квітень",
    5: "травень",
    6: "червень",
    7: "липень",
    8: "серпень",
    10: "жовтень",
    11: "листопад",
    12: "грудень",
    9: "вересень",
}

lift = 0


@dp.callback_query_handler(text_contains="search_task")
async def start_choosing(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    prin = call.data
    print(prin)
    await TaskSelector.start.set()
    await year_choose(call, state)


@dp.callback_query_handler(text_contains="search_task", state = TaskSelector.start)
async def year_choose(call: types.CallbackQuery, state: FSMContext):
    year_choise = InlineKeyboardMarkup(row_width=1)
    tasks = await db.get_all_tasks()
    count = dict()
    await TaskSelector.year.set()

    if not tasks:
        await call.message.answer("У вас немає жодної задачі")
        await state.finish()
        return

    for task in tasks:
        year = task.datetime.year
        count[year] = count.get(year, 0) + 1

    if len(count.keys()) == 1:
        for key in count.keys():
            call2 = call
            call2.data = f"choose_year:{key}"
            print(call2.data)
            await month_choose(call2, state)

    for k,v in count.items():
        year_choise.insert(
            InlineKeyboardButton(
                text=f"{k} рік ({v} задач)",
                callback_data=f"choose_year:{k}"
                                )
        )
    year_choise.insert(cancel_btn)
    await call.message.answer(
        "Шукаємо задачу.\n"
        , reply_markup=year_choise)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_year", state = TaskSelector.year)
async def month_choose(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await TaskSelector.month.set()
    year = int(call.data.split(':')[-1])
    await state.update_data(year=year)
    tasks = await db.get_tasks_where(year)
    count = dict()
    month_choise = InlineKeyboardMarkup(row_width=1)

    for task in tasks:
        month = task.datetime.month
        count[month] = count.get(month, 0) + 1

    if len(count.keys()) == 1:
        for key in count.keys():
            global lift
            if not lift:
                lift = "month"
            call2 = call
            call2.data = f"choose_month:{key}"
            print(call2.data)
            await week_choose(call2, state)
            return

    for k,v in count.items():
        month_choise.insert(
            InlineKeyboardButton(
                text=f"{dict_of_month[k]} ({v} задач)",
                callback_data=f"choose_month:{k}"
            )
        )
    month_choise.insert(back_btn)
    month_choise.insert(cancel_btn)
    await call.message.answer(
        f"Шукаємо задачу. в {year} році\n"
        , reply_markup=month_choise)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_month", state = TaskSelector.month)
async def week_choose(call: CallbackQuery, state: FSMContext):
    print("week_choose")
    await call.answer(cache_time=60)
    await TaskSelector.week.set()
    year = (await state.get_data()).get('year')
    month = int(call.data.split(':')[-1])
    await state.update_data(month=month)
    tasks = await db.get_tasks_where(year, month)
    count = dict()
    week_choise = InlineKeyboardMarkup(row_width=1)
    left, right = split_on_week(tasks[0].datetime)
    #left = [date+datetime.timedelta(days=-1) for date in left]
    for i in range(len(left)):
        tasks = await db.get_tasks(left[i], right[i])
        key = f"{left[i].day}-{right[i].day}"
        print(key)
        for task in tasks:
           count[key] = count.get(key,0) + 1

    print(count)

    if len(count.keys()) == 1:
        for key in count.keys():
            global lift
            if not lift:
                lift = "week"
            call2 = call
            call2.data = f"choose_week:{key}"
            print(call2.data)
            await day_choose(call2, state)
            return

    for k,v in count.items():
        week_choise.insert(
            InlineKeyboardButton(
                text=f"{k} тиждень ({v} задач)",
                callback_data=f"choose_week:{k}"
                                )
        )
    week_choise.insert(back_btn)
    week_choise.insert(cancel_btn)
    await call.message.answer(
        f"Шукаємо задачу в {year}.{month} місяці\n"
        , reply_markup=week_choise)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_week", state = TaskSelector.week)
async def day_choose(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await TaskSelector.day.set()
    year = (await state.get_data()).get('year')
    month = (await state.get_data()).get('month')
    week = call.data.split(':')[-1]
    start_day, end_day = week.split('-')
    start_day, end_day =  int(start_day), int(end_day)
    await state.update_data(week=week)
    count = dict()
    day_choise = InlineKeyboardMarkup(row_width=1)

    print(start_day,":", end_day)
    if (start_day < end_day):
        start = datetime.datetime(year= year, month = month, day = start_day)
        end = datetime.datetime(year= year, month = month, day = end_day) + datetime.timedelta(days=1)
    else:
        start = datetime.datetime(year=year, month=month, day=start_day)
        year, month = (year + 1, 1) if (month + 1) == 13 else (year, month + 1)
        end = datetime.datetime(year=year, month=(month+1), day=end_day) + datetime.timedelta(days=1)
    tasks = await db.get_tasks(start, end)

    for task in tasks:
        this_day = task.datetime.day
        count[this_day] = count.get(this_day, 0) + 1

    if len(count.keys()) == 1:
        for key in count.keys():
            global lift
            if not lift:
                lift = "task"
            call2 = call
            call2.data = f"choose_day:{key}"
            print(call2.data)
            await task_choose(call2, state)

            return

    for k,v in count.items():
        day_choise.insert(
            InlineKeyboardButton(
                text=f"{month}.{k} число ({v} задач)",
                callback_data=f"choose_day:{k}"
                                )
        )
    day_choise.insert(back_btn)
    day_choise.insert(cancel_btn)
    await call.message.answer(
        f"Шукаємо задачу в {year}.{month} місяці\n"
        , reply_markup=day_choise)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_day", state = TaskSelector.day)
async def task_choose(call: CallbackQuery, state: FSMContext):
    print("start task_choose")
    await TaskSelector.task.set()
    await call.answer(cache_time=60)
    year = (await state.get_data()).get('year')
    month = (await state.get_data()).get('month')
    day = int(call.data.split(':')[-1])
    await state.update_data(day=day)
    task_choise = InlineKeyboardMarkup(row_width=1)
    tasks = await db.get_tasks_where(year, month, day)

    for task in tasks:
        print(f"choose_task:{task.id}")
        task_choise.insert(
            InlineKeyboardButton(
                text=f"<b>{task.get_datetime_str()}</b> - {task.name}",
                callback_data=f"choose_task:{task.id}"
            )
        )
    task_choise.insert(back_btn)
    task_choise.insert(cancel_btn)
    await call.message.answer(
        f"Шукаємо задачу в {year}.{month}.{day} \n"
        , reply_markup=task_choise)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_task", state = TaskSelector.task)
async def final(call: CallbackQuery, state: FSMContext):
    await TaskSelector.final.set()
    await call.answer(cache_time=60)
    id = int(call.data.split(':')[-1])

    task = await db.get_task(id)
    message = f"<b> {task.name} </b>\n" \
              f"<i> {task.get_datetime_str()} </i>\n" \
              f" {task.description}"

    task_action = InlineKeyboardMarkup(row_width=1)
    task_action.insert(InlineKeyboardButton(text="Редагувати", callback_data=f"red:{id}"))
    task_action.insert(InlineKeyboardButton(text="Видалити", callback_data=f"del:{id}"))
    task_action.insert(cancel_btn)

    await call.message.answer(message, reply_markup=task_action)

    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()


@dp.callback_query_handler(text_contains="choose_task", state = "*")
async def final(call: CallbackQuery, state: FSMContext):
    await TaskSelector.final.set()
    await call.answer(cache_time=60)
    id = int(call.data.split(':')[-1])
    task = await db.get_task(id)
    message = f"<b> {task.name} </b>\n" \
              f"<i> {task.get_datetime_str()} </i>\n" \
              f" {task.description}"

    task_action = InlineKeyboardMarkup(row_width=1)
    task_action.insert(InlineKeyboardButton(text="Редагувати", callback_data=f"red:{id}"))
    task_action.insert(InlineKeyboardButton(text="Видалити", callback_data=f"del:{id}"))
    task_action.insert(cancel_btn)

    await call.message.answer(message, reply_markup=task_action)


@dp.callback_query_handler(text_contains="back", state = "*")
async def back(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print("left start", await state.get_state())
    call.data = "back2"

    if lift:
        if lift == "month":
            print("left month")
            await state.set_state(TaskSelector.month)
            await TaskSelector.month.set()
            await back_month(call, state)

        if lift == "week" or lift == "day":
            print("left week")
            await state.set_state(TaskSelector.day)
            await TaskSelector.day.set()
            await back_day(call, state)

        if lift == "task":
            print("left task")
            await state.set_state(TaskSelector.task)
            await TaskSelector.task.set()
            await back_task(call, state)

        if lift == "final":
            print("left final")
            await state.set_state(TaskSelector.final)
            await TaskSelector.final.set()
            await back_final(call, state)

    else:
        if state.get_state() == TaskSelector.month.state:
            await back_month(call, state)
        if state.get_state() == TaskSelector.week.state:
            await back_day(call, state)
        if state.get_state() == TaskSelector.day.state:
            await back_day(call, state)
        if state.get_state() == TaskSelector.task.state:
            await back_task(call, state)
        if state.get_state() == TaskSelector.final.state:
            await back_final(call, state)



@dp.callback_query_handler(text_contains="back2", state = TaskSelector.month)
async def back_month(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print("state == TaskSelector.month")
    await TaskSelector.start.set()
    await year_choose(call, state)


@dp.callback_query_handler(text_contains="back2", state = TaskSelector.week)
@dp.callback_query_handler(text_contains="back2", state = TaskSelector.day)
async def back_day(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print("state == TaskSelector.week or state == TaskSelector.day")
    await TaskSelector.year.set()
    year = (await state.get_data()).get("year")
    call.data = f"choose_year:{year}"
    await month_choose(call, state)


@dp.callback_query_handler(text_contains="back2", state = TaskSelector.task)
async def back_task(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print("state == TaskSelector.task")
    await TaskSelector.week.set()
    week = (await state.get_data()).get("week")
    call.data = f"choose_week:{week}"
    await day_choose(call, state)


@dp.callback_query_handler(text_contains="back2", state = TaskSelector.final)
async def back_final(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    print("state == TaskSelector.final")
    await TaskSelector.day.set()
    day = (await state.get_data()).get("day")
    call.data = f"choose_day:{day}"
    await task_choose(call, state)