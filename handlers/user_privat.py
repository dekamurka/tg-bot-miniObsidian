from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from kbds import reply  
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Note
from database.orm_query import orm_get_products, orm_delete_product
from kbds.inline import get_callback_btns
from database.orm_query import (
    orm_add_product,
    orm_delete_product,
    orm_get_product,
    orm_get_products,
    orm_update_product,
)
user_router = Router()

class Addnote(StatesGroup):
    name = State() 
    description = State()  

@user_router.message(F.text.lower().contains('старт'))
@user_router.message(F.text.lower().contains('нача'))
@user_router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет, это виртуальный помощник для создания заметок. \nНапишите свой запрос.", reply_markup=reply.start_kb)


@user_router.message(F.text.lower().contains('список'))
@user_router.message(F.text.lower().contains('заметки'))
@user_router.message(F.text.lower().contains('check'))
@user_router.message(F.text.lower().contains('проверить'))
@user_router.message(Command('check'))
async def check_notes(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id  # Идентификатор пользователя
    print(f"Получаем заметки для пользователя: {user_id}")  # Логирование user_id
    
    try:
        products = await orm_get_products(session, user_id=user_id)  # Фильтрация заметок по user_id
        print(f"Найдено заметок: {len(products)}")  # Логирование количества заметок
        
        if not products:
            await message.answer("Список заметок пуст.")
        else:
            for product in products:
                await message.answer(f"*Название:* *{product.name}*\n*Описание:* {product.description}", 
                                     parse_mode="Markdown", 
                                     reply_markup=get_callback_btns(btns={
                                         'Удалить': f'delete_{product.id}'
                                     }))
            await message.answer("Это все ваши заметки.")
    except Exception as e:
        print(f"Ошибка при получении заметок: {e}")  # Логирование ошибок
        await message.answer("Произошла ошибка при получении списка заметок.")

@user_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))
    await callback.answer("Заметка удалена")
    await callback.message.answer("Заметка удалена!")

@user_router.message(StateFilter(None), F.text.lower().contains('сдела'))
@user_router.message(StateFilter(None), F.text.lower().contains('созда'))
@user_router.message(StateFilter(None), F.text.lower().contains('creat'))
@user_router.message(StateFilter(None), Command('create'))
async def menu(message: types.Message, state: FSMContext):
    await message.answer("Введите название заметки", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Addnote.name)

@user_router.message(Addnote.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer("Вы отменили создание заметки", reply_markup=reply.start_kb)
        return
    
    await state.update_data(name=message.text)  
    await message.answer("Введите описание заметки", reply_markup=reply.dop_kb)
    await state.set_state(Addnote.description)

@user_router.message(Addnote.description, F.text)
async def process_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer("Вы отменили создание заметки", reply_markup=reply.start_kb)
        return
    
    user_data = await state.get_data()
    description = message.text
    user_data['description'] = description

    user_id = message.from_user.id

    obj = Note(
        name=user_data.get("name"),
        description=user_data.get("description"),
        user_id=user_id 
    )
    
    session.add(obj)
    await session.commit()

    name = user_data.get("name")
    await message.answer(f"Заметка '{name}' создана!", reply_markup=reply.start_kb) 
    
    await state.clear()

@user_router.message(StateFilter('*'), F.text.lower().contains("отмена"))
@user_router.message(StateFilter('*'), Command('cancel'))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены.")
        return

    await state.clear()
    await message.answer("Вы отменили действия", reply_markup=reply.start_kb)

@user_router.message()
async def handle_unknown_command(message: types.Message):
    await message.reply("Команда не распознана. Пожалуйста, убедитесь в правильности команды и попробуйте снова!")
