import random
from db import models

ADMIN_TELEGRAM_ID = 84747865  # آی‌دی عددی شما

def generate_otp():
    return random.randint(10000, 99999)

async def send_otp_to_admin(bot, otp):
    await bot.send_message(ADMIN_TELEGRAM_ID, f"کد ورود به پنل ادمین:\n{otp}")

def export_users_txt():
    users = models.get_all_users()
    filename = "users.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for user in users:
            f.write(f"{user['email']} - {user['phone']}\n")
    return filename

def export_searches_txt():
    searches = models.get_all_searches()
    filename = "searches.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for s in searches:
            f.write(f"{s['user']}: {s['query']} ({s['dt']})\n")
    return filename