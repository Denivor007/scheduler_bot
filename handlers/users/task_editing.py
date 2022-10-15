from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import choice, cancel

from utils.db_api.comands import DBCommands

from .default import start
from loader import dp
import datetime
from states.task_edit import TaskEditor
from states.task_selection import TaskSelector
from utils.misc.task_datatime import data_checker, to_datatime


db = DBCommands()

text = ""
task_id = 0


@dp.callback_query_handler(text_contains="red", state = TaskSelector.final)
async def enter_test(call: types.CallbackQuery, state = FSMContext):
    await call.answer(cache_time=60)
    print("enter test")
    global task_id
    task_id = int(call.data.split(':')[-1])
    task = await db.get_task(task_id)
    global text
    text = "_Підказка: Ви можете використувувати текст нижче для копіювання_\n"\
              f"дата - `{task.get_datetime_str()}`\n"\
              f"назва - `{task.name}`\n"\
              f"опис - `{task.description}`\n"
    await call.message.answer("Редагуємо вашу задачу!\n"
                              "Введіть нову дату\n\n"
                              + text,
                              parse_mode=types.ParseMode.MARKDOWN,
                              reply_markup= cancel)
    await state.finish()
    await TaskEditor.Q1.set()


@dp.message_handler(state=TaskEditor.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    error = data_checker(answer)
    global text
    if not error:
        await state.update_data(task_data=answer)

        await message.answer("Редагуємо вашу задачу!\n"
                             "Введіть нову дату\n\n"
                             + text,
                             parse_mode=types.ParseMode.MARKDOWN,
                             reply_markup=cancel)
        await TaskEditor.next()
    else:
        await message.answer(f"УПС\n{error}"+text,
                                parse_mode = types.ParseMode.MARKDOWN, reply_markup= cancel)

        await TaskEditor.Q2.set()


@dp.message_handler(state=TaskEditor.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text
    if (len(answer) > 32):
        await message.answer("УПС\n"
                             f"Розмір вашої назви {len(answer)} символи, а потрібно ДО 32"+text,
                                parse_mode = types.ParseMode.MARKDOWN,
                                reply_markup= cancel)

        await TaskEditor.Q2.set()
    else:
        await message.answer("Редагуємо вашу задачу!\n"
                             "Введіть детальний опис задачі!\n\n"
                             + text,
                             parse_mode=types.ParseMode.MARKDOWN,
                             reply_markup=cancel)
        await state.update_data(task_name=answer)
        await TaskEditor.Q3.set()


@dp.message_handler(state=TaskEditor.Q3)
async def answer_q3(message: types.Message, state: FSMContext):
    # Достаем переменные
    data = await state.get_data()
    task_data = to_datatime(data.get("task_data"))
    task_name = data.get("task_name")
    task_desctiption = message.text
    text = f"<i>{task_data}</i> \n{task_name}:\n{task_desctiption}"
    await db.add_new_task(task_data, task_name, task_desctiption)
    result = await db.delete_task(task_id)

    await message.answer(text, reply_markup=cancel)

    await state.finish()

    # Вариант завершения 2
    # await state.reset_state()

    # Вариант завершения 3 - без стирания данных в data
    # await state.reset_state(with_data=False)
