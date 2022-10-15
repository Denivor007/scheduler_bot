from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from utils.weather_api.weather_api import *


from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.main_menu import choice, cancel

from utils.db_api.comands import DBCommands

from loader import dp
import datetime
from states.sity_set import SetSity
from utils.misc.task_datatime import data_checker, to_datatime


db = DBCommands()


@dp.callback_query_handler(text_contains="set_city")
async def set_city1(call: types.CallbackQuery):
    this_user = types.User.get_current()
    await call.message.answer(text=f"Привіт, {this_user.first_name}!\n"
                              f"Здається я досі не знаю звідки ти (не переймайся, це виключно для прогнозу погоди)\n"
                              f"Введи своє місто!\n", reply_markup=cancel)
    await SetSity.Q1.set()


@dp.message_handler(Command('set_city'))
async def set_city2(message: types.Message):
    this_user = types.User.get_current()
    await message.answer(text=f"Привіт, {this_user.first_name}!\n"
                              f"Здається я досі не знаю звідки ти (не переймайся, це виключно для прогнозу погоди)\n"
                              f"Введи своє місто!\n", reply_markup=cancel)
    await SetSity.Q1.set()


@dp.message_handler(state=SetSity.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    from google_trans_new import google_translator
    Translator = google_translator()

    user = types.User.get_current()
    answer = message.text
    city_t = Translator.translate(answer, lang_tgt='en')
    city_t = city_t.lower()
    if city_checker(city_t):
        await db.set_city(user.id, city_t)
        await state.finish()
        usr = await db.get_user(user.id)
        text = "Чудово! це моє олюблене місто, і там зараз он яка погода\n"
        text += get_weather(usr[0].city)
        await message.answer(text=text, reply_markup=choice)
    else:
        await message.answer(text=f"{user.first_name}, "
                                  f"Такого міста я не знаю(\n"
                                  f"Можливо вам допоможуть наступні поради:\n"
                                  f"1. Перевірте правильність набору\n"
                                  f"2. Спробуйте увести найблищий обласний центр\n"
                                  f"3. Спробуйте увести англійською",
                                    reply_markup=cancel)
        await SetSity.Q1.set()

