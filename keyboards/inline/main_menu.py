from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import menu_callback

choice = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Створити нову справу📝", callback_data=menu_callback.new(
                action = "create_task"
            ))
        ],
        [
            InlineKeyboardButton(text="Обрати справу📝", callback_data=menu_callback.new(
                action = "search_task"
            ))
        ]
    ]
)


choice_сity = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Створити нову справу📝", callback_data=menu_callback.new(
                action = "create_task"
            ))
        ],
        [
            InlineKeyboardButton(text="Обрати справу📝", callback_data=menu_callback.new(
                action = "search_task"
            ))
        ],
    [
        InlineKeyboardButton(text="Додати місто", callback_data=menu_callback.new(
                action = "set_city"
            ))
    ]]
)

cancel_btn = InlineKeyboardButton(text="Меню", callback_data=menu_callback.new(
                action = "cancel"
            ))
back_btn = InlineKeyboardButton(text="Назад", callback_data="back")

cancel = InlineKeyboardMarkup(
    inline_keyboard=[[
            cancel_btn
    ],
        ])

