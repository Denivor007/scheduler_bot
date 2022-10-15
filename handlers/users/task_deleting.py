from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import *

from utils.db_api.comands import DBCommands

from .default import start
from loader import dp
import datetime
from states.task_selection import TaskSelector
from utils.misc.task_datatime import data_checker, to_datatime

db = DBCommands()


@dp.callback_query_handler(text_contains="del", state = TaskSelector.final)
async def delete_test(call: types.CallbackQuery, state = FSMContext):
    print("delete_test")
    await call.answer(cache_time=60)
    task_id = int(call.data.split(':')[-1])
    await db.delete_task(task_id)
    await call.message.answer("Задачу було видалено",
                              reply_markup=cancel)
    await state.finish()

