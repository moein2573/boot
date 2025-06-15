from aiogram import types
from bot.utils import generate_otp, send_otp_to_admin, export_users_txt, export_searches_txt
from db import models

admin_otps = {}
admin_logged_in = set()  # set of chat_ids

def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("لیست کاربران", callback_data="admin_users"),
        types.InlineKeyboardButton("دانلود کاربران", callback_data="admin_export_users"),
        types.InlineKeyboardButton("جستجوهای محبوب", callback_data="admin_popular_searches"),
        types.InlineKeyboardButton("دانلود جستجوها", callback_data="admin_export_searches"),
        types.InlineKeyboardButton("خروج", callback_data="admin_logout")
    )
    return kb

async def handle_admin_command(message, bot):
    chat_id = message.chat.id
    otp = generate_otp()
    admin_otps[chat_id] = otp
    await send_otp_to_admin(bot, otp)
    await message.reply("کد ورود یکبار مصرف به پنل ادمین برای شما ارسال شد.\nلطفا کد را وارد کنید:")

async def handle_admin_otp(message):
    chat_id = message.chat.id
    otp = admin_otps.get(chat_id)
    if otp and message.text.strip() == str(otp):
        admin_logged_in.add(chat_id)
        await message.reply("ورود موفق! منوی مدیریت:", reply_markup=admin_keyboard())
    else:
        await message.reply("کد اشتباه است. دوباره تلاش کنید.")

async def handle_admin_callback(callback_query):
    chat_id = callback_query.message.chat.id
    if chat_id not in admin_logged_in:
        await callback_query.message.edit_text("دسترسی ندارید، ابتدا وارد شوید.")
        return

    data = callback_query.data
    if data == "admin_users":
        users = models.get_all_users()
        if not users:
            await callback_query.message.edit_text("هیچ کاربری ثبت نشده.", reply_markup=admin_keyboard())
            return
        text = "\n".join([f"{idx+1}. {u['email']} - {u['phone']}" for idx, u in enumerate(users)])
        await callback_query.message.edit_text(text, reply_markup=admin_keyboard())
    elif data == "admin_export_users":
        file = export_users_txt()
        await callback_query.message.answer_document(types.input_file.InputFile(file), caption="لیست کاربران", reply_markup=admin_keyboard())
    elif data == "admin_popular_searches":
        searches = models.get_popular_searches()
        if not searches:
            await callback_query.message.edit_text("جستجویی ثبت نشده.", reply_markup=admin_keyboard())
            return
        text = "\n".join([f"{idx+1}. {s['query']} ({s['count']} بار)" for idx, s in enumerate(searches)])
        await callback_query.message.edit_text(text, reply_markup=admin_keyboard())
    elif data == "admin_export_searches":
        file = export_searches_txt()
        await callback_query.message.answer_document(types.input_file.InputFile(file), caption="لیست جستجوها", reply_markup=admin_keyboard())
    elif data == "admin_logout":
        admin_logged_in.discard(chat_id)
        await callback_query.message.edit_text("از پنل مدیریت خارج شدید.")