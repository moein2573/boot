import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from db import models
from bot import handlers, admin

API_TOKEN = '7590167834:AAFs65ugRa8Y6GVA3C3xFfLe40gK4_9RIGM'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# اطمینان از وجود پوشه db
os.makedirs('db', exist_ok=True)
models.init_db()

# --- کاربر ---
@dp.message_handler(commands=['start', 'new'])
async def start_cmd(message: types.Message):
    await handlers.start_handler(message)

@dp.message_handler(lambda message: handlers.get_user_state(message.chat.id) == 'email')
async def email_handler(message: types.Message):
    await handlers.get_email(message)

@dp.message_handler(lambda message: handlers.get_user_state(message.chat.id) == 'phone')
async def phone_handler(message: types.Message):
    await handlers.get_phone(message)

@dp.message_handler(lambda message: handlers.get_user_state(message.chat.id) == 'search', content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def search_handler(message: types.Message):
    await handlers.search_handler(message)

@dp.callback_query_handler(lambda c: c.data in ['next_page', 'prev_page'])
async def pagination_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    state = handlers.user_states[chat_id]
    page = state.get('page', 0)
    results = state.get('results', [])
    if callback_query.data == 'next_page':
        page += 1
    else:
        page = max(0, page - 1)
    handlers.user_states[chat_id]['page'] = page
    await handlers.send_results(callback_query.message, chat_id, page, results)
    await callback_query.answer()

# --- ادمین ---
@dp.message_handler(commands=['admin'])
async def admin_cmd(message: types.Message):
    await admin.handle_admin_command(message, bot)

@dp.message_handler(lambda message: message.chat.id in admin.admin_otps and message.chat.id not in admin.admin_logged_in)
async def admin_otp_handler(message: types.Message):
    await admin.handle_admin_otp(message)

@dp.callback_query_handler(lambda c: c.data.startswith('admin_'))
async def admin_menu_callback(callback_query: types.CallbackQuery):
    await admin.handle_admin_callback(callback_query)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
