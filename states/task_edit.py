from aiogram.dispatcher.filters.state import StatesGroup, State

class TaskEditor(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()