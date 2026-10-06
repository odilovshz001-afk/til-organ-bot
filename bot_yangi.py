import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a): pass

Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), H).serve_forever(), daemon=True).start()

import telebot, random, json, time, re
from telebot import types
from datetime import datetime, timedelta

try:
    from deep_translator import GoogleTranslator
    TARJIMA_BOR = True
except:
    TARJIMA_BOR = False

T = "8774189119:AAGM1_wXOJ_pGwkyYKSIdgkOSWPVoudTn6M"
A = 8178917212

REKLAMA_MATN = "📢 *Bizni kuzatib boring!*\n\n📸 Instagram: @odilov03_\n💬 Telegram: @odilov0_3\n\n━━━━━━━━━━━━━━━━\n🤖 Til o'rganish boti"

def reklama_btn():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("📸 Instagram", url="https://instagram.com/odilov03_"),
        types.InlineKeyboardButton("💬 Telegram", url="https://t.me/odilov0_3")
    )
    return m

bot = telebot.TeleBot(T)
U, R, D, F, SV, TT = {}, {}, {}, {}, {}, {}
kor = set()
S = []

for f in ["sozlar.json","sozlar_katta.json","sozlar_qoshimcha.json","sozlar_ish.json","sozlar_vaqt.json"]:
    if os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
            for s in d["sozlar"]:
                if s["ru"] not in kor:
                    S.append(s); kor.add(s["ru"])
        except: pass

for fname in ["users.json","reyting.json","kunlik.json","dostlar.json","sevimlilar.json","talablar.json"]:
    if os.path.exists(fname):
        try:
            data = json.load(open(fname, encoding="utf-8"))
            if fname == "users.json": U = data
            elif fname == "reyting.json": R = data
            elif fname == "kunlik.json": D = data
            elif fname == "dostlar.json": F = data
            elif fname == "sevimlilar.json": SV = data
            elif fname == "talablar.json": TT = data
        except: pass

# ===== KUNDALIK GAPLAR =====
KUNDALIK_GAPLAR = []
for fname in ["kundalik_gaplar.json", "kundalik_gaplar2.json"]:
    if os.path.exists(fname):
        try:
            d = json.load(open(fname, encoding="utf-8"))
            KUNDALIK_GAPLAR.extend(d["gaplar"])
            print(f"✅ {fname}: {len(d['gaplar'])} ta")
        except: pass
print(f"📚 JAMI kundalik gaplar: {len(KUNDALIK_GAPLAR)} ta")

SUHBAT_GAPLAR = {
    "💼 Ishda": [
        {"ru": "Доброе утро!", "uz": "Xayrli tong!"},
        {"ru": "Как ваши дела?", "uz": "Ishlaringiz qanday?"},
        {"ru": "Что нового?", "uz": "Nima yangilik?"},
        {"ru": "Я готов к работе.", "uz": "Men ishga tayyorman."},
        {"ru": "Давайте начнём.", "uz": "Keling, boshlaymiz."},
        {"ru": "Сколько времени?", "uz": "Soat necha?"},
        {"ru": "Мне нужно закончить работу.", "uz": "Ishni tugatishim kerak."},
        {"ru": "Хорошего дня!", "uz": "Yaxshi kun tilayman!"},
        {"ru": "До завтра!", "uz": "Ertagagacha!"},
        {"ru": "Спасибо за помощь.", "uz": "Yordamingiz uchun rahmat."}
    ],
    "🚶 Ko'chada": [
        {"ru": "Извините, как пройти?", "uz": "Kechirasiz, qanday boriladi?"},
        {"ru": "Где находится метро?", "uz": "Metro qayerda joylashgan?"},
        {"ru": "Это далеко?", "uz": "Bu uzoqmi?"},
        {"ru": "Сколько стоит такси?", "uz": "Taksi qancha turadi?"},
        {"ru": "Остановите здесь, пожалуйста.", "uz": "Shu yerda to'xtating, iltimos."},
        {"ru": "Я заблудился.", "uz": "Men adashib qoldim."},
        {"ru": "Помогите, пожалуйста.", "uz": "Yordam bering, iltimos."},
        {"ru": "Где выход?", "uz": "Chiqish qayerda?"},
        {"ru": "Спасибо большое!", "uz": "Katta rahmat!"},
        {"ru": "До свидания!", "uz": "Xayr!"}
    ],
    "🛒 Do'konda": [
        {"ru": "Сколько это стоит?", "uz": "Bu qancha turadi?"},
        {"ru": "Это дорого.", "uz": "Bu qimmat."},
        {"ru": "Есть дешевле?", "uz": "Arzonroq bormi?"},
        {"ru": "Дайте, пожалуйста.", "uz": "Bering, iltimos."},
        {"ru": "Можно картой?", "uz": "Karta bilan bo'ladimi?"},
        {"ru": "Спасибо за покупку!", "uz": "Xaridingiz uchun rahmat!"},
        {"ru": "Где касса?", "uz": "Kassa qayerda?"},
        {"ru": "Дайте чек, пожалуйста.", "uz": "Chek bering, iltimos."},
        {"ru": "Хорошего дня!", "uz": "Yaxshi kun tilayman!"},
        {"ru": "Приходите ещё!", "uz": "Yana keling!"}
    ],
    "☕ Suhbatda": [
        {"ru": "Привет! Как дела?", "uz": "Salom! Qalaysiz?"},
        {"ru": "Меня зовут...", "uz": "Mening ismim..."},
        {"ru": "Очень приятно!", "uz": "Juda yoqimli!"},
        {"ru": "Откуда вы?", "uz": "Qayerdansiz?"},
        {"ru": "Я из Узбекистана.", "uz": "Men O'zbekistondanman."},
        {"ru": "Сколько вам лет?", "uz": "Yoshingiz nechada?"},
        {"ru": "Что вы любите?", "uz": "Nimani yaxshi ko'rasiz?"},
        {"ru": "Давайте встретимся.", "uz": "Keling, uchrashamiz."},
        {"ru": "Какой у вас номер?", "uz": "Raqamingiz qanday?"},
        {"ru": "До встречи!", "uz": "Ko'rishguncha!"}
    ],
    "🏥 Shifokorda": [
        {"ru": "Мне плохо.", "uz": "O'zimni yomon his qilyapman."},
        {"ru": "У меня болит голова.", "uz": "Boshim og'riyapti."},
        {"ru": "У меня температура.", "uz": "Haroratim bor."},
        {"ru": "Вызовите врача.", "uz": "Shifokor chaqiring."},
        {"ru": "Где аптека?", "uz": "Dorixona qayerda?"},
        {"ru": "Мне нужна помощь.", "uz": "Menga yordam kerak."},
        {"ru": "Скорая помощь!", "uz": "Tez yordam!"},
        {"ru": "Спасибо, доктор!", "uz": "Rahmat, doktor!"}
    ],
    "📞 Telefonda": [
        {"ru": "Алло!", "uz": "Allo!"},
        {"ru": "Кто это?", "uz": "Bu kim?"},
        {"ru": "Можно...?", "uz": "...mumkinmi?"},
        {"ru": "Позвоните позже.", "uz": "Keyinroq qo'ng'iroq qiling."},
        {"ru": "Я перезвоню.", "uz": "Men qayta qo'ng'iroq qilaman."},
        {"ru": "Не слышно.", "uz": "Eshitilmayapti."},
        {"ru": "Говорите громче.", "uz": "Balandroq gapiring."},
        {"ru": "До свидания!", "uz": "Xayr!"}
    ]
}

KATEGORIYALAR = {
    "👋 Salomlashish": ["Привет","Спасибо","Пожалуйста","Да","Нет","Здравствуйте","До свидания","Как дела?"],
    "🍞 Oziq-ovqat": ["Вода","Хлеб","Чай","Кофе","Молоко","Мясо","Рыба","Фрукт","Овощ"],
    "👨‍👩‍👧 Oila": ["Мама","Папа","Брат","Сестра","Семья","Друг"],
    "💼 Ish": ["Работа","Учитель","Ученик","Книга","Стол","Стул"],
    "🏙 Shahar": ["Город","Страна","Язык","Дом","Машина"],
    "⏰ Vaqt": ["Время","День","Ночь","Утро","Вечер"]
}

GAPLAR = [
    {"togri":"Я люблю чай","sozlar":["чай","люблю","Я"],"tarjima":"Men choyni yaxshi ko'raman"},
    {"togri":"Меня зовут Али","sozlar":["Али","зовут","Меня"],"tarjima":"Mening ismim Ali"},
    {"togri":"Как дела","sozlar":["дела","Как"],"tarjima":"Qalaysan"},
    {"togri":"Я хочу воду","sozlar":["воду","хочу","Я"],"tarjima":"Men suv xohlayman"},
    {"togri":"Спасибо большое","sozlar":["большое","Спасибо"],"tarjima":"Katta rahmat"}
]

GRAMMATIKA = {
    "📘 Fe'l zamonlari": "Настоящее: Я читаю\nПрошедшее: Я читал\nБудущее: Я буду читать",
    "📗 Kelishiklar": "Им: стол\nРод: стола\nДат: столу\nВин: стол\nТвор: столом\nПред: о столе",
    "📙 Sonlar": "1 один\n2 два\n3 три\n4 четыре\n5 пять\n6 шесть\n7 семь\n8 восемь\n9 девять\n10 десять",
    "📕 Ranglar": "красный — qizil\nсиний — ko'k\nзелёный — yashil\nжёлтый — sariq\nчёрный — qora\nбелый — oq"
}

CHAT_SAVOLLAR = [
    {"savol":"Как тебя зовут?","javob":"Меня зовут..."},
    {"savol":"Откуда ты?","javob":"Я из..."},
    {"savol":"Сколько тебе лет?","javob":"Мне ... лет"},
    {"savol":"Что ты любишь?","javob":"Я люблю..."},
    {"savol":"Где ты живёшь?","javob":"Я живу в..."}
]

print(f"📚 JAMI so'zlar: {len(S)} ta")

st = {}

def saqlash(): json.dump(U, open("users.json","w",encoding="utf-8"), ensure_ascii=False)
def reyting_saqlash(): json.dump(R, open("reyting.json","w",encoding="utf-8"), ensure_ascii=False)
def kunlik_saqlash(): json.dump(D, open("kunlik.json","w",encoding="utf-8"), ensure_ascii=False)
def dostlar_saqlash(): json.dump(F, open("dostlar.json","w",encoding="utf-8"), ensure_ascii=False)
def sevimlilar_saqlash(): json.dump(SV, open("sevimlilar.json","w",encoding="utf-8"), ensure_ascii=False)
def talablar_saqlash(): json.dump(TT, open("talablar.json","w",encoding="utf-8"), ensure_ascii=False)

def ball_qosh(user_id, ball):
    uid = str(user_id)
    R[uid] = R.get(uid, 0) + ball
    reyting_saqlash()

def ism_tekshir(ism):
    if not ism or len(ism) < 2: return False
    if not re.match(r'^[\w\s\'-]{2,50}$', ism, re.UNICODE): return False
    if ism.strip().isdigit(): return False
    return True

def telefon_tekshir(tel):
    tel_toza = re.sub(r'[^\d+]', '', tel)
    if re.match(r'^\+?\d{10,15}$', tel_toza): return True
    return False

def sana_tekshir(sana):
    try:
        d = datetime.strptime(sana, "%d.%m.%Y")
        yosh = datetime.now().year - d.year
        if 5 <= yosh <= 120: return True
    except: pass
    return False

def kunlik_tekshir(user_id):
    uid = str(user_id)
    bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D:
        D[uid] = {"oxirgi_kun":bugun,"streak":1,"challenge":False,"sovga":False}
        kunlik_saqlash(); return 1
    if D[uid]["oxirgi_kun"] == bugun: return D[uid]["streak"]
    kecha = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    if D[uid]["oxirgi_kun"] == kecha: D[uid]["streak"] += 1
    else: D[uid]["streak"] = 1
    D[uid]["oxirgi_kun"] = bugun; D[uid]["challenge"] = False; D[uid]["sovga"] = False
    kunlik_saqlash(); return D[uid]["streak"]

def daraja(ball):
    if ball >= 5000: return "👑 C2"
    if ball >= 3000: return "🥇 C1"
    if ball >= 1500: return "🥈 B2"
    if ball >= 500: return "🥉 B1"
    if ball >= 100: return "📗 A2"
    return "📘 A1"

def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📅 Kundalik","📚 Flashcard","🎯 Testlar","🎮 O'yin")
    m.add("💬 Suhbat","📝 Gap tuzish","📚 Kategoriya","🎵 Talaffuz")
    m.add("🎁 Sovga","👥 Do'stlar","⭐ Sevimlilar","🏆 Reyting")
    m.add("📖 Grammatika","💬 Chat","📊 Statistika","🔄 Tarjima")
    m.add("📢 Talab va taklif","ℹ️ Yordam")
    return m

def suhbat_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in SUHBAT_GAPLAR.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish","✅ Bilaman","❌ Bilmayman","⭐ Saqlash")
    m.add("🔊 Eshitish","⏹ To'xtatish")
    return m

def tarjima_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇷🇺 Ruscha → 🇺🇿 O'zbekcha","🇺🇿 O'zbekcha → 🇷🇺 Ruscha","⬅️ Orqaga")
    return m

def reyting_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🥇 TOP-10","📊 Mening reytingim","🏅 Yutuqlarim")
    m.add("📊 Grafik statistika","⬅️ Orqaga")
    return m

def kategoriya_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in KATEGORIYALAR.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def gap_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("⏹ To'xtatish")
    return m

def dost_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("🔗 Havola","👥 Do'stlarim","🏆 Do'stlar reytingi","⬅️ Orqaga")
    return m

def gram_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in GRAMMATIKA.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def talab_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("📢 Talab/taklif yozish","📋 Mening talablarim","⬅️ Orqaga")
    return m

def kundalik_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🔊 Eshitish","🔄 Yangilash")
    m.add("⬅️ Orqaga")
    return m

def reklama_yubor():
    while True:
        time.sleep(3600)
        try:
            for uid in list(U.keys()):
                try:
                    bot.send_message(int(uid), REKLAMA_MATN, parse_mode='Markdown', reply_markup=reklama_btn())
                    time.sleep(0.1)
                except: pass
        except: pass

Thread(target=reklama_yubor, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "👑 Admin\n\n/royxat\n/talablar"); return
    if c in U and U[c].get("ism"):
        streak = kunlik_tekshir(m.chat.id)
        ball_qosh(m.chat.id, 1)
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, f"Salom, {U[c]['ism']}! 👋\n\n📚 {len(S)} ta so'z\n💬 {len(KUNDALIK_GAPLAR)} ta gap\n🔥 Streak: {streak} kun\n🏆 Ball: {R.get(c,0)}\n🎁 +1 ball!", reply_markup=menu())
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","sana_tugilgan":"","tel":"","h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, "🌍 Assalomu alaykum!\n\n📝 Ismingizni kiriting:\n_(Har qanday alifboda)_", parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['royxat'])
def royxat(m):
    if m.chat.id != A: return
    txt = f"👥 Foydalanuvchilar: {len(U)}\n\n"
    for uid, u in list(U.items())[:20]:
        txt += f"• {u.get('ism','?')} {u.get('familiya','')} — {R.get(uid,0)} ball\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(commands=['talablar'])
def talablar_admin(m):
    if m.chat.id != A: return
    if not TT:
        bot.send_message(m.chat.id, "📭 Talablar yo'q."); return
    txt = f"📢 *Talablar:* {len(TT)} ta\n\n"
    for i, (uid, talab) in enumerate(list(TT.items())[-20:], 1):
        ism = U.get(uid, {}).get("ism", "?")
        txt += f"{i}. {ism}:\n{talab['matn']}\n\n"
    bot.send_message(m.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda m: str(m.chat.id) in U and U[str(m.chat.id)].get("h"))
def reg(m):
    c = str(m.chat.id); u = U[c]; t = m.text.strip()
    if u["h"] == "ism":
        if not ism_tekshir(t):
            bot.send_message(c, "❌ Ism noto'g'ri!\nKamida 2 harf.\nQaytadan:"); return
        u["ism"] = t; u["h"] = "fam"; saqlash()
        bot.send_message(c, "✅ Familiyangizni kiriting:")
    elif u["h"] == "fam":
        if not ism_tekshir(t):
            bot.send_message(c, "❌ Familiya noto'g'ri!\nKamida 2 harf.\nQaytadan:"); return
        u["familiya"] = t; u["h"] = "sana"; saqlash()
        bot.send_message(c, "✅ Tug'ilgan sana:\n\nFormat: `DD.MM.YYYY`", parse_mode='Markdown')
    elif u["h"] == "sana":
        if not sana_tekshir(t):
            bot.send_message(c, "❌ Sana noto'g'ri!\n\nFormat: `DD.MM.YYYY`\nMasalan: `15.05.1995`\nQaytadan:", parse_mode='Markdown'); return
        u["sana_tugilgan"] = t; u["h"] = "tel"; saqlash()
        bot.send_message(c, "✅ Telefon:\n\nFormat: `+XXXXXXXXXXXX`", parse_mode='Markdown')
    elif u["h"] == "tel":
        if not telefon_tekshir(t):
            bot.send_message(c, "❌ Telefon noto'g'ri!\n\nMasalan: `+998901234567`\nQaytadan:"); return
        u["tel"] = t; u["h"] = ""; saqlash()
        ball_qosh(m.chat.id, 5); kunlik_tekshir(m.chat.id)
        bot.send_message(c, f"🎉 Rahmat, {u['ism']}!\n\n🎁 +5 ball!")
        bot.send_message(c, REKLAMA_MATN, parse_mode='Markdown', reply_markup=reklama_btn())
        try: bot.send_message(A, f"👤 YANGI:\n{u['ism']} {u['familiya']}\n{u['sana_tugilgan']}\n{u['tel']}")
        except: pass
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, "Menyu:", reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def hand(m):
    c = str(m.chat.id); t = m.text
    if m.chat.id == A: return
    if c not in U or not U[c].get("ism") or U[c].get("h"): return
    if c not in st: st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
    x = st[c]

    # KUNDALIK
    if x.get("kundalik_gaplar"):
        if t == "🔄 Yangilash":
            kundalik_gaplar(c); return
        if t == "🔊 Eshitish":
            gaplar = x.get("kundalik_gaplar", [])
            for g in gaplar[:3]:
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={g['ru']}&tl=ru&client=tw-ob"
                    bot.send_voice(c, url)
                    time.sleep(0.5)
                except: pass
            return
        if t == "⬅️ Orqaga":
            x["kundalik_gaplar"] = None; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return

    # TALAB
    if x.get("talab"):
        if t == "⬅️ Orqaga":
            x["talab"] = False; x["talab_yozish"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "📢 Talab/taklif yozish":
            x["talab_yozish"] = True; st[c] = x
            bot.send_message(c, "📢 *Talab yoki taklifingizni yozing:*", parse_mode='Markdown')
            return
        if t == "📋 Mening talablarim":
            mening = TT.get(c, {}).get("matn", "Yo'q")
            bot.send_message(c, f"📋 *Sizning talabingiz:*\n\n{mening}", parse_mode='Markdown')
            return
        if x.get("talab_yozish"):
            TT[c] = {"matn": t, "sana": datetime.now().strftime("%d.%m.%Y %H:%M")}
            talablar_saqlash()
            bot.send_message(c, "✅ *Rahmat!*", parse_mode='Markdown', reply_markup=menu())
            try: bot.send_message(A, f"📢 *YANGI TALAB*\n\n{U[c].get('ism','?')}:\n{t}")
            except: pass
            x["talab_yozish"] = False; x["talab"] = False; st[c] = x
            return
        return

    # SUHBAT
    if x.get("suhbat_kat"):
        if t == "🔊 Eshitish":
            kat = x["suhbat_kat"]; i = x.get("suhbat_i", 0)
            gap = SUHBAT_GAPLAR[kat][i]["ru"]
            try:
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={gap}&tl=ru&client=tw-ob"
                bot.send_voice(c, url)
            except: pass
            return
        if t == "➡️ Keyingi":
            x["suhbat_i"] = x.get("suhbat_i", 0) + 1; st[c] = x
            suhbat_korsat(c); return
        if t == "⬅️ Oldingi":
            x["suhbat_i"] = max(0, x.get("suhbat_i", 0) - 1); st[c] = x
            suhbat_korsat(c); return
        if t == "⬅️ Orqaga":
            x["suhbat_kat"] = None; st[c] = x
            bot.send_message(c, "Suhbat:", reply_markup=suhbat_menu()); return

    if x.get("suhbat"):
        if t == "⬅️ Orqaga":
            x["suhbat"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in SUHBAT_GAPLAR:
            x["suhbat_kat"] = t; x["suhbat_i"] = 0; st[c] = x
            suhbat_korsat(c)
        return

    # GAP TUZISH
    if x.get("gap"):
        if t == "⏹ To'xtatish":
            x["gap"] = False; st[c] = x
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if t.strip().lower() == x.get("gap_togri","").lower():
            ball_qosh(m.chat.id, 15)
            bot.send_message(c, f"✅ To'g'ri! +15 ball\n🏆 Jami: {R.get(c,0)}")
            x["gap"] = False; st[c] = x
            bot.send_message(c, "Yana o'ynash uchun «📝 Gap tuzish» ni bosing.", reply_markup=menu())
        else: bot.send_message(c, f"❌ Noto'g'ri. To'g'ri: {x.get('gap_togri','')}")
        return

    # KATEGORIYA
    if x.get("kat"):
        if t == "⬅️ Orqaga":
            x["kat"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in KATEGORIYALAR:
            txt = f"📚 *{t}*\n\n"
            for i, rus in enumerate(KATEGORIYALAR[t], 1):
                for s in S:
                    if s["ru"] == rus: txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
            bot.send_message(c, txt, parse_mode='Markdown')
        return

    # GRAMMATIKA
    if x.get("gram"):
        if t == "⬅️ Orqaga":
            x["gram"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in GRAMMATIKA:
            bot.send_message(c, f"📖 *{t}*\n\n{GRAMMATIKA[t]}", parse_mode='Markdown')
        return

    # DO'STLAR
    if x.get("dost"):
        if t == "⬅️ Orqaga":
            x["dost"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🔗 Havola":
            link = f"https://t.me/Til_organ_uz_bot?start={c}"
            bot.send_message(c, f"🔗 *Havolangiz:*\n\n`{link}`\n\n+50 ball!", parse_mode='Markdown')
        elif t == "👥 Do'stlarim":
            dostlar = F.get(c, [])
            if not dostlar: bot.send_message(c, "Do'stlaringiz yo'q.")
            else:
                txt = "👥 *Do'stlaringiz:*\n\n"
                for i, d in enumerate(dostlar, 1):
                    txt += f"{i}. {U.get(d,{}).get('ism','?')} — {R.get(d,0)} ball\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        elif t == "🏆 Do'stlar reytingi":
            dostlar = F.get(c, [])
            if not dostlar: bot.send_message(c, "Do'stlar yo'q.")
            else:
                ballar = [(d, R.get(d,0)) for d in dostlar + [c]]
                ballar.sort(key=lambda x: x[1], reverse=True)
                txt = "🏆 *Do'stlar:*\n\n"
                for i, (d, b) in enumerate(ballar, 1):
                    ism = U.get(d,{}).get("ism","?") if d != c else "Siz"
                    txt += f"{i}. {ism} — {b} ball\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        return

    # TALAFFUZ
    if x.get("talaffuz"):
        if t == "⏹ To'xtatish":
            x["talaffuz"] = None; st[c] =