from aiogram import types
from db import models
from bot.scraper import search_products

user_states = {}

def get_user_state(chat_id):
    return user_states.get(chat_id, {}).get('step', 'email')

def set_user_state(chat_id, step, extra=None):
    user_states.setdefault(chat_id, {})['step'] = step
    if extra:
        user_states[chat_id].update(extra)

async def start_handler(message):
    chat_id = message.chat.id
    set_user_state(chat_id, 'email')
    await message.answer("به kalafinder خوش آمدید!\nلطفاً ایمیل خود را وارد کنید:")

async def get_email(message):
    chat_id = message.chat.id
    email = message.text.strip()
    set_user_state(chat_id, 'phone', {'email': email})
    await message.answer("شماره تماس خود را وارد کنید:")

async def get_phone(message):
    chat_id = message.chat.id
    phone = message.text.strip()
    email = user_states[chat_id]['email']
    models.save_user(chat_id, email, phone)
    set_user_state(chat_id, 'search')
    await message.answer("نام یا مدل کالای موردنظر را ارسال کنید:")

async def search_handler(message):
    chat_id = message.chat.id
    step = get_user_state(chat_id)
    if step != 'search':
        return
    if message.content_type == types.ContentType.TEXT:
        query = message.text.strip()
    elif message.content_type == types.ContentType.PHOTO:
        await message.reply("در حال حاضر فقط جستجوی متنی فعال است.")
        return
    else:
        await message.reply("نوع ورودی نامعتبر است.")
        return

    models.save_search(chat_id, query)
    await message.reply("در حال جستجو ...")
    results = search_products(query)
    if not results:
        await message.reply("کالایی یافت نشد یا مشکل در ارتباط با سایت فروشگاهی وجود دارد.")
        return

    user_states[chat_id]['results'] = results
    user_states[chat_id]['page'] = 0
    await send_results(message, chat_id, 0, results)

async def send_results(message, chat_id, page, results):
    start = page * 10
    end = start + 10
    page_results = results[start:end]
    text = ""
    for idx, r in enumerate(page_results):
        text += f"{idx+1+start}. [{r['title']}]({r['link']}) - {r['price']}\n"
    buttons = []
    if end < len(results):
        buttons.append(types.InlineKeyboardButton("صفحه بعد", callback_data="next_page"))
    if page > 0:
        buttons.append(types.InlineKeyboardButton("صفحه قبل", callback_data="prev_page"))
    kb = types.InlineKeyboardMarkup().add(*buttons) if buttons else None
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=kb)