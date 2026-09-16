import telebot
import requests
from telebot import types

BOT_TOKEN = "8868163699:AAFJo1kIbDvdMcDKsv3g06yav2FNAkaJLXk"
ADMIN_ID = 7166502503   # ✅ Sandesh का Telegram User ID

PHONE_API = "https://ansh-apis.is-dev.org/api/new"
PHONE_KEY = "ansh"
AADHAR_API = "https://ansh-apis.is-dev.org/api/ration"
AADHAR_KEY = "luffy"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== USER DATA =====
user_search_count = {}
premium_users = set()

def check_limit(user_id):
    if user_id in premium_users:
        return True
    count = user_search_count.get(user_id, 0)
    if count >= 2:
        return False
    else:
        user_search_count[user_id] = count + 1
        return True

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    banner = (
        "╭━━━〔 ✨ cyber_.mind ✨ 〕━━━╮\n"
        "┃ 📌 Welcome Boss\n"
        "┃ Let's Start Investigation of Phone Number & Aadhar card Details.\n"
        "┃ ⚡ Designed by: Sandesh Kumar\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📱 Phone Number", callback_data="phone")
    btn2 = types.InlineKeyboardButton("🆔 Aadhar Details", callback_data="aadhar")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, banner, reply_markup=markup)

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "phone":
        bot.send_message(call.message.chat.id, "🔍 Send me a phone number:")
        bot.register_next_step_handler(call.message, lookup_phone)
    elif call.data == "aadhar":
        bot.send_message(call.message.chat.id, "🔍 Send me an Aadhar ID:")
        bot.register_next_step_handler(call.message, lookup_aadhar)

# ===== PREMIUM MESSAGE =====
def send_premium_message(chat_id, user_id):
    bot.send_message(chat_id,
        "⚠️ Free limit (2 searches) खत्म हो गया है!\n\n"
        "🌐 Premium Plans:\n"
        "💰 1 Day → ₹20\n"
        "💰 1 Week → ₹120\n\n"
        "👉 नीचे दिए गए QR code से payment करो और screenshot admin को भेजो।\n"
        f"🆔 आपका User ID: {user_id} (admin को भेजना होगा)"
    )
    try:
        with open("qr.png", "rb") as qr:
            bot.send_photo(chat_id, qr, caption="📷 Scan and Pay via UPI")
    except:
        bot.send_message(chat_id, "⚠️ QR code image नहीं मिला। कृपया admin से संपर्क करें।")

# ===== ADMIN APPROVAL =====
@bot.message_handler(commands=['approve'])
def approve(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            premium_users.add(user_id)
            bot.send_message(user_id, "✅ Admin ने आपका premium activate कर दिया है! अब unlimited searches available हैं।")
            bot.reply_to(message, f"User {user_id} को premium दे दिया गया।")
        except:
            bot.reply_to(message, "⚠️ Command format: /approve <user_id>")
    else:
        bot.reply_to(message, "⚠️ सिर्फ admin approve कर सकता है।")

# ===== PHONE LOOKUP =====
def lookup_phone(message):
    user_id = message.from_user.id
    if not check_limit(user_id):
        send_premium_message(message.chat.id, user_id)
        return

    num = message.text.strip()
    params = {"key": PHONE_KEY, "num": num}
    try:
        response = requests.get(PHONE_API, params=params, timeout=15)
        data = response.json()
        if "Results" in data and len(data["Results"]) > 0:
            info = data["Results"][0]
            result = (
                f"📱 Phone Lookup Result:\n"
                f"👤 Name: {info.get('name','—')}\n"
                f"👨‍👩‍👦 Father: {info.get('fname','—')}\n"
                f"🏠 Address: {info.get('address','—')}\n"
                f"📞 Mobile: {info.get('mobile','—')}\n"
                f"🌐 Circle: {info.get('circle','—')}\n"
                f"🆔 ID: {info.get('id','—')}\n"
                f"✉️ Email: {info.get('email','—')}\n"
            )
        else:
            result = "❌ No phone data found."
        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ API Error: {str(e)}")

# ===== AADHAR LOOKUP =====
def lookup_aadhar(message):
    user_id = message.from_user.id
    if not check_limit(user_id):
        send_premium_message(message.chat.id, user_id)
        return

    aadhar_id = message.text.strip()
    params = {"key": AADHAR_KEY, "id": aadhar_id}
    try:
        response = requests.get(AADHAR_API, params=params, timeout=15)
        data = response.json()
        if "pd" in data:
            pd = data["pd"]
            members = pd.get("memberDetailsList", [])
            member_text = "".join([f"👤 {m.get('memberName','—')} ({m.get('relationship_name','—')})\n" for m in members])
            result = (
                f"🆔 Aadhar Lookup Result:\n"
                f"🏠 Address: {pd.get('address','—')}\n"
                f"📍 District: {pd.get('homeDistName','—')}\n"
                f"🌐 State: {pd.get('homeStateName','—')}\n"
                f"📑 RC ID: {pd.get('rcId','—')}\n"
                f"📋 Scheme: {pd.get('schemeName','—')}\n\n"
                f"👨‍👩‍👧 Members:\n{member_text}"
            )
        else:
            result = "❌ No Aadhar data found."
        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ API Error: {str(e)}")

print("🤖 Bot is running...")
bot.polling()
