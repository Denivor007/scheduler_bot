from aiogram.dispatcher.filters.state import StatesGroup, State


class TaskSelector(StatesGroup):
    start = State()
    year = State()
    month = State()
    week = State()
    day = State()
    task = State()
    final = State()

