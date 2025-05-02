import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from handlers.user_privat import user_router  
from middlewares.db import DataBaseSession  
from database.orm_query import orm_get_products, orm_delete_product    

load_dotenv(find_dotenv())

from database.engine import create_db, drop_db, session_maker 

ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']


bot = Bot(token=os.getenv('TOKEN'))


dp = Dispatcher()
dp.include_router(user_router) 


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db() 

    await create_db() 


async def on_shutdown(bot):
    print('Что-то сломалось, но мы уже работаем!')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown) 
    dp.update.middleware(DataBaseSession(session_pool=session_maker))  

    await create_db() 
    await bot.delete_webhook(drop_pending_updates=True)  
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)  

# Запуск бота
asyncio.run(main())
