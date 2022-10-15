from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import choice, cancel

from utils.db_api.comands import DBCommands

from .default import start
from loader import dp
import datetime
from states.task_create import TaskCreator
from utils.misc.task_datatime import data_checker, to_datatime


db = DBCommands()


@dp.callback_query_handler(text_contains="create_task")
async def enter_test(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer("Створюємо нову задачу.\n" + "Введіть дату у форматі рррр-мм-дд чч:хх"
                              , reply_markup= cancel)
    await TaskCreator.Q1.set()


@dp.message_handler(state=TaskCreator.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    error = data_checker(answer)
    if not error:
        await state.update_data(task_data=answer)

        await message.answer("Введіть назву задачі (до 32 символів)"
                              , reply_markup= cancel)
        await TaskCreator.next()
    else:
        await message.answer(f"УПС\n{error}", reply_markup= cancel)
        await TaskCreator.Q1.set()


@dp.message_handler(state=TaskCreator.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text
    if (len(answer) > 32):
        await message.answer("УПС\n"
                             f"Розмір вашої назви {len(answer)} символи, а потрібно ДО 32"
                              , reply_markup= cancel)
        await TaskCreator.Q2.set()
    else:
        await message.answer(f"Введить детальний опис задачі"
                              , reply_markup= cancel)
        await state.update_data(task_name=answer)
        await TaskCreator.Q3.set()


@dp.message_handler(state=TaskCreator.Q3)
async def answer_q3(message: types.Message, state: FSMContext):
    # Достаем переменные
    await message.answer(f"Нагадування має прийти за... (hh:mm)"
                         , reply_markup=cancel)
    await state.update_data(task_desctiption=message.text)

    await TaskCreator.Q4.set()


@dp.message_handler(state=TaskCreator.Q4)
async def answer_q4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_data = to_datatime(data.get("task_data"))
    task_name = data.get("task_name")
    task_desctiption = data.get("task_desctiption")
    delay = message.text
    try:
        h,m = delay.split(":")
        total = int(h)*60 + int(m)
    except:
        await message.answer("УПС\n"
                             f"Некоректне уведення"
                             , reply_markup=cancel)
        await TaskCreator.Q4.set()
    text = f"<i>{task_data}</i> - {task_name}:\n{task_desctiption}\n нагадати за {delay}"
    try:
        await db.add_new_task(task_data, task_name, task_desctiption, total )
    except:
        print("не вышло почему-то")
    await message.answer(text)
    await state.finish()
