import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== SOXTA VEB-SERVER (Render uchun) =====
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

Thread(target=run_health_server, daemon=True).start()

# ===== BOT KODI =====
import telebot
from telebot import types
import time
import random
import json
from datetime import datetime

TOKEN = "8774189119:AAGM1_wXOJ_pGwkyYKSIdgkOSWPVoudTn6M"
ADMIN_ID = 8178917212

bot = telebot.TeleBot(TOKEN)

USERS_FAYL = "users.json"

def users_yuklash():
    if os.path.exists(USERS_FAYL):
        try:
            with open(USERS_FAYL, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def users_saqlash(users):
    with open(USERS_FAYL, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

USERS = users_yuklash()

RUS_SOZLAR = []
korilgan = set()

FAYLLAR = [
    "sozlar.json",
    "sozlar_katta.json",
    "sozlar_qoshimcha.json",
    "sozlar_ish.json",
    "sozlar_vaqt.json"
]

for fayl in FAYLLAR:
    if os.path.exists(fayl):
        try:
            with open(fayl, "r", encoding="utf-8") as f:
                data = json.load(f)
                for soz in data["sozlar"]:
                    if soz["ru"] not in korilgan:
                        RUS_SOZLAR.append(soz)
                        korilgan.add(soz["ru"])
        except:
            pass

print(f"JAMI: {len(RUS_SOZLAR)} ta so'z")

user_state = {}

def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        types.KeyboardButton("📅 Kundalik so'zlar"),
        types.KeyboardButton("📚 Flashcard"),
        types.KeyboardButton("🎯 Testlar"),
        types.KeyboardButton("📖 Barcha so'zlar"),
        types.KeyboardButton("📊 Statistika"),
        types.KeyboardButton("ℹ️ Yordam")
    )
    return m

def flashcard_buttons():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        types.KeyboardButton("👁 Ko'rsatish"),
        types.KeyboardButton("✅ Bilaman"),
        types.KeyboardButton("❌ Bilmayman"),
        types.KeyboardButton("⏹ To'xtatish")
    )
    return m

def test_buttons(variantlar):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for v in variantlar:
        m.add(types.KeyboardButton(v["uz"]))
    m.add(types.KeyboardButton("⏹ Testdan chiqish"))
    return m

def barcha_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        types.KeyboardButton("⬅️ Oldingi 20"),
        types.KeyboardButton("➡️ Keyingi 20"),
        types.KeyboardButton("⬅️ Orqaga")
    )
    return m

def adminga_xabar_yuborish(user):
    if ADMIN_ID == 0:
        return
    text = (
        f"YANGI FOYDALANUVCHI!\n\n"
        f"Ism: {user['ism']}\n"
        f"Familiya: {user['familiya']}\n"
        f"Telefon: {user['telefon']}\n"
        f"ID: {user['id']}\n"
        f"Sana: {user['sana']}"
    )
    try:
        bot.send_message(ADMIN_ID, text)
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    cid = str(message.chat.id)
    
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Admin panel\n\n/royxat - Foydalanuvchilar")
        return
    
    if cid in USERS and USERS[cid].get("ism"):
        user_state[cid] = {"index": 0, "score": 0, "total": 0, "active": False, "barcha_sahifa": 0, "test_active": False}
        text = f"Salom, {USERS[cid]['ism']}! \n\n{len(RUS_SOZLAR)} ta so'z mavjud.\n\nTugmalardan birini tanlang"
        bot.send_message(message.chat.id, text, reply_markup=main_menu())
        return
    
    USERS[cid] = {
        "id": message.chat.id,
        "ism": "",
        "familiya": "",
        "telefon": "",
        "holat": "ism_kutilmoqda",
        "sana": datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    users_saqlash(USERS)
    
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum!\n\nBotdan foydalanish uchun malumotlaringizni kiriting.\n\nIsmingizni kiriting:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(commands=['royxat'])
def royxat(message):
    if message.chat.id != ADMIN_ID:
        return
    if not USERS:
        bot.send_message(message.chat.id, "Foydalanuvchilar yo'q.")
        return
    text = f"FOYDALANUVCHILAR ({len(USERS)} ta)\n\n"
    for uid, u in USERS.items():
        text += f"{u['ism']} {u['familiya']}\n{u['telefon']}\nID: {u['id']}\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: str(m.chat.id) in USERS and USERS[str(m.chat.id)].get("holat"))
def royxat_handler(message):
    cid = str(message.chat.id)
    user = USERS[cid]
    text = message.text.strip()
    
    if user["holat"] == "ism_kutilmoqda":
        user["ism"] = text
        user["holat"] = "familiya_kutilmoqda"
        users_saqlash(USERS)
        bot.send_message(message.chat.id, "Familiyangizni kiriting:")
    
    elif user["holat"] == "familiya_kutilmoqda":
        user["familiya"] = text
        user["holat"] = "telefon_kutilmoqda"
        users_saqlash(USERS)
        bot.send_message(message.chat.id, "Telefon raqamingizni kiriting:\n\nMasalan: +998901234567")
    
    elif user["holat"] == "telefon_kutilmoqda":
        user["telefon"] = text
        user["holat"] = ""
        users_saqlash(USERS)
        bot.send_message(message.chat.id, f"Rahmat, {user['ism']}!\n\nEndi botdan foydalanishingiz mumkin.\n\n{len(RUS_SOZLAR)} ta so'z mavjud.")
        adminga_xabar_yuborish(user)
        user_state[cid] = {"index": 0, "score": 0, "total": 0, "active": False, "barcha_sahifa": 0, "test_active": False}
        bot.send_message(message.chat.id, "Tugmalardan birini tanlang", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(message):
    cid = str(message.chat.id)
    
    if message.chat.id == ADMIN_ID:
        return
    
    if cid not in USERS or not USERS[cid].get("ism") or USERS[cid].get("holat"):
        return
    
    text = message.text
    if cid not in user_state:
        user_state[cid] = {"index": 0, "score": 0, "total": 0, "active": False, "barcha_sahifa": 0, "test_active": False}
    st = user_state.get(cid, {})

    if text == "⏹ Testdan chiqish":
        st["test_active"] = False
        user_state[cid] = st
        bot.send_message(cid, "Test to'xtatildi.", reply_markup=main_menu())
        return

    if st.get("test_active") and st.get("current_answer"):
        togri = st["current_answer"]
        if text == togri:
            st["test_score"] = st.get("test_score", 0) + 1
            st["test_total"] = st.get("test_total", 0) + 1
            st["test_index"] = st.get("test_index", 0) + 1
            user_state[cid] = st
            bot.send_message(cid, "Togri!")
            show_test(cid)
        elif text in [s["uz"] for s in RUS_SOZLAR]:
            st["test_total"] = st.get("test_total", 0) + 1
            st["test_index"] = st.get("test_index", 0) + 1
            user_state[cid] = st
            bot.send_message(cid, f"Notogri. Togri: {togri}")
            show_test(cid)
        return

    if text == "📅 Kundalik so'zlar":
        kundalik_sozlar(cid)
    elif text == "📚 Flashcard":
        user_state[cid] = {"index": 0, "score": 0, "total": 0, "active": True, "barcha_sahifa": 0, "test_active": False}
        show_flashcard(cid)
    elif text == "🎯 Testlar":
        start_test(cid)
    elif text == "📖 Barcha so'zlar":
        barcha_korsat(cid, 0)
    elif text == "⬅️ Oldingi 20":
        sh = st.get("barcha_sahifa", 0) - 1
        if sh < 0:
            bot.send_message(cid, "Birinchi sahifa.")
        else:
            barcha_korsat(cid, sh)
    elif text == "➡️ Keyingi 20":
        sh = st.get("barcha_sahifa", 0) + 1
        js = (len(RUS_SOZLAR) + 19) // 20
        if sh >= js:
            bot.send_message(cid, "Oxirgi sahifa.")
        else:
            barcha_korsat(cid, sh)
    elif text == "📊 Statistika":
        bot.send_message(cid, f"Statistika\n\nJami: {len(RUS_SOZLAR)}\nKorilgan: {st.get('index', 0)}\nTogri: {st.get('score', 0)}")
    elif text == "ℹ️ Yordam":
        bot.send_message(cid, "Yordam")
    elif text == "👁 Ko'rsatish":
        st = user_state.get(cid, {})
        idx = st.get("index", 0)
        if idx < len(RUS_SOZLAR):
            s = RUS_SOZLAR[idx]
            bot.send_message(cid, f"Tarjima:\n\n{s['ru']} -> {s['uz']}", reply_markup=flashcard_buttons())
    elif text == "✅ Bilaman":
        st = user_state.get(cid, {})
        st["score"] = st.get("score", 0) + 1
        st["total"] = st.get("total", 0) + 1
        st["index"] = st.get("index", 0) + 1
        user_state[cid] = st
        show_flashcard(cid)
    elif text == "❌ Bilmayman":
        st = user_state.get(cid, {})
        st["total"] = st.get("total", 0) + 1
        st["index"] = st.get("index", 0) + 1
        user_state[cid] = st
        show_flashcard(cid)
    elif text == "⏹ To'xtatish":
        st = user_state.get(cid, {})
        st["active"] = False
        user_state[cid] = st
        bot.send_message(cid, "To'xtatildi.", reply_markup=main_menu())
    elif text == "⬅️ Orqaga":
        st["test_active"] = False
        user_state[cid] = st
        bot.send_message(cid, "Asosiy menyu", reply_markup=main_menu())
    else:
        bot.send_message(cid, "Tugmalardan birini tanlang", reply_markup=main_menu())

def kundalik_sozlar(cid):
    kun = datetime.now().day
    gs = 10
    jg = max(1, len(RUS_SOZLAR) // gs)
    gi = kun % jg
    sozlar = RUS_SOZLAR[gi * gs:(gi + 1) * gs]
    text = f"Kundalik so'zlar - {datetime.now().strftime('%d.%m.%Y')}\n\n"
    for i, s in enumerate(sozlar, 1):
        text += f"{i}. {s['ru']} - {s['uz']}\n\n"
    bot.send_message(cid, text)

def barcha_korsat(cid, sahifa=0):
    ss = 20
    jami = len(RUS_SOZLAR)
    js = (jami + ss - 1) // ss
    if sahifa < 0: sahifa = 0
    if sahifa >= js: sahifa = js - 1
    sozlar = RUS_SOZLAR[sahifa * ss:(sahifa + 1) * ss]
    text = f"Barcha so'zlar - {sahifa + 1}/{js}\n\n"
    for i, s in enumerate(sozlar, sahifa * ss + 1):
        text += f"{i}. {s['ru']} - {s['uz']}\n\n"
    text += f"Sahifa: {sahifa + 1}/{js}"
    st = user_state.get(cid, {})
    st["barcha_sahifa"] = sahifa
    user_state[cid] = st
    bot.send_message(cid, text, reply_markup=barcha_menu())

def show_flashcard(cid):
    st = user_state.get(cid, {})
    idx = st.get("index", 0)
    if idx >= len(RUS_SOZLAR):
        bot.send_message(cid, "Tugadi!", reply_markup=main_menu())
        return
    s = RUS_SOZLAR[idx]
    bot.send_message(cid, f"Flashcard ({idx + 1}/{len(RUS_SOZLAR)})\n\nRuscha: {s['ru']}", reply_markup=flashcard_buttons())

def start_test(cid):
    user_state[cid] = {"test_index": 0, "test_score": 0, "test_total": 0, "test_active": True, "current_answer": None}
    show_test(cid)

def show_test(cid):
    st = user_state.get(cid, {})
    idx = st.get("test_index", 0)
    if idx >= len(RUS_SOZLAR):
        sc = st.get("test_score", 0)
        tt = st.get("test_total", 0)
        st["test_active"] = False
        user_state[cid] = st
        bot.send_message(cid, f"Test tugadi!\n\nJami: {tt}\nTogri: {sc}", reply_markup=main_menu())
        return
    togri = RUS_SOZLAR[idx]
    boshqa = [s for s in RUS_SOZLAR if s["uz"] != togri["uz"]]
    if len(boshqa) < 3:
        bot.send_message(cid, "So'zlar kam.")
        return
    notogri = random.sample(boshqa, 3)
    variantlar = [togri] + notogri
    random.shuffle(variantlar)
    st["current_answer"] = togri["uz"]
    user_state[cid] = st
    bot.send_message(cid, f"Test ({idx + 1}/{len(RUS_SOZLAR)})\n\n{togri['ru']} - ?", reply_markup=test_buttons(variantlar))

print("Bot ishga tushdi...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print("Xatolik:", e)
        time.sleep(5)