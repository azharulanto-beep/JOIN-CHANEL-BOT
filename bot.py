import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import random
import string
import time
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# ====================== YOUR CHANNEL ======================
CHANNEL_LINK = "https://t.me/+olOzQqzfF9A1MTVl"
CHANNEL_USERNAME = "@Udusus"
APK_FILE_PATH = "app.apk"
IMAGE_URL = "https://i.postimg.cc/qvt6CQjk/logo.jpg"

bot = telebot.TeleBot(TOKEN)

# ====================== DATABASE ======================
def load_db(f):
    try:
        with open(f, 'r') as file:
            return json.load(file)
    except:
        return {}

def save_db(f, d):
    with open(f, 'w') as file:
        json.dump(d, file, indent=4)

users = load_db('users.json')

# ====================== CHECK JOINED ======================
def check_joined(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ====================== GENERATE KEY ======================
def gen_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# ====================== START ======================
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    
    if uid in users and users[uid].get("got_key", False):
        bot.send_message(m.chat.id, f"🔑 YOUR KEY: `{users[uid]['key']}`", parse_mode="Markdown")
        return
    
    # Small welcome like screenshot
    bot.send_message(m.chat.id, "HELLO MODDER ANTO ❤️", parse_mode="Markdown")
    time.sleep(0.5)
    
    bot.send_message(m.chat.id, "JOIN ALL CHANNELS FIRST AND TAKE YOUR PAID PANEL 1 DAY TRIAL KEY 🎁", parse_mode="Markdown")
    time.sleep(0.5)
    
    bot.send_message(m.chat.id, "HOW TO GENERATE KEY 🔑\nCLICK HERE", parse_mode="Markdown")
    time.sleep(0.5)
    
    bot.send_photo(m.chat.id, IMAGE_URL, caption="🖼️ PAID PANEL PREVIEW", parse_mode="Markdown")
    time.sleep(0.5)
    
    # Show channel list
    text = """- JOIN CHANNEL 1"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 JOIN CHANNEL", url=CHANNEL_LINK))
    markup.add(InlineKeyboardButton("✅ VERIFY JOINED", callback_data="verify"))
    
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    if check_joined(c.message.chat.id):
        uid = str(c.message.chat.id)
        key = gen_key()
        
        users[uid] = {
            "name": c.message.from_user.first_name,
            "key": key,
            "got_key": True,
            "date": str(datetime.now())
        }
        save_db('users.json', users)
        
        bot.send_message(c.message.chat.id, f"✅ VERIFIED!\n\n🔑 YOUR KEY: `{key}`", parse_mode="Markdown")
        
        # Send APK
        try:
            with open(APK_FILE_PATH, 'rb') as f:
                bot.send_document(c.message.chat.id, f, caption="📱 YOUR APK FILE", parse_mode="Markdown")
        except:
            pass
    else:
        text = """❌ NOT JOINED YET!

- JOIN CHANNEL FIRST
- THEN CLICK VERIFY"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 JOIN CHANNEL", url=CHANNEL_LINK))
        markup.add(InlineKeyboardButton("✅ VERIFY AGAIN", callback_data="verify"))
        
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

# ====================== ADMIN ======================
@bot.message_handler(commands=['admin'])
def admin(m):
    if m.chat.id != ADMIN_ID:
        return
    total = len(users)
    got = sum(1 for u in users.values() if u.get("got_key", False))
    bot.send_message(m.chat.id, f"👑 ADMIN PANEL\n\nUSERS: {total}\nGOT KEY: {got}\nPENDING: {total - got}")

@bot.message_handler(commands=['users'])
def users_list(m):
    if m.chat.id != ADMIN_ID:
        return
    if not users:
        bot.reply_to(m, "NO USERS")
        return
    text = "👥 USERS:\n\n"
    for uid, u in users.items():
        text += f"{uid} | {u.get('name')} | {u.get('key')}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return
    msg = m.text.replace("/broadcast ", "")
    c = 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"📢 {msg}")
            c += 1
        except:
            pass
    bot.reply_to(m, f"SENT TO {c} USERS")

# ====================== RUN ======================
print("🔥 BOT STARTED!")
bot.infinity_polling()
