from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_kb = ReplyKeyboardMarkup (
    keyboard=[
        [
            KeyboardButton(text="Создать заметку"),
            KeyboardButton(text="Посмотреть список заметок"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите команду'
)

dop_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Желаете продолжить?'
)

del_kbd = ReplyKeyboardRemove()