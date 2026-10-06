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

REKLAMA_MATN = "📢 Bizni kuzatib boring!\n\n📸 Instagram: @odilov03_\n💬 Telegram: @odilov0_3"

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

KUNDALIK_GAPLAR = []
for fname in ["kundalik_gaplar.json", "kundalik_gaplar2.json"]:
    if os.path.exists(fname):
        try:
            d = json.load(open(fname, encoding="utf-8"))
            KUNDALIK_GAPLAR.extend(d["gaplar"])
        except: pass

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

st = {}

def saqlash(): json.dump(U, open("users.json","w",encoding="utf-8"), ensure_ascii=False)
def reyting_saqlash(): json.dump(R, open("reyting.json","w",encoding="utf-8"), ensure_ascii=False)
def kunlik_saqlash(): json.dump(D, open("kunlik.json","w",encoding="utf-8"), ensure_ascii=False)
def dostlar_saqlash(): json.dump(F, open("dostlar.json","w",encoding="utf-8"), ensure_ascii=False)
def sevimlilar_saqlash(): json.dump(SV, open("sevimlilar.json","w",encoding="utf-8"), ensure_ascii=False)
def talablar_saqlash(): json.dump(TT, open("talablar.json","w",encoding="utf-8"), ensure_ascii=False)

def ball_qosh(uid, ball):
    R[str(uid)] = R.get(str(uid), 0) + ball
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

def kunlik_tekshir(uid):
    uid = str(uid)
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

def kundalik_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🔊 Eshitish","🔄 Yangilash")
    m.add("⬅️ Orqaga")
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

def gap_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("⏹ To'xtatish")
    return m

def kundalik_gaplar(c):
    if not KUNDALIK_GAPLAR:
        bot.send_message(c, "Gaplar bazasi yoq."); return
    gaplar = random.sample(KUNDALIK_GAPLAR, min(10, len(KUNDALIK_GAPLAR)))
    txt = f"💬 Kundalik muloqot gaplari\n📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    for i, g in enumerate(gaplar, 1):
        txt += f"{i}. 🇷🇺 {g['ru']}\n     🇺🇿 {g['uz']}\n\n"
    txt += f"🎁 +1 ball\n🏆 Jami: {R.get(c, 0)}\n\n"
    txt += f"📚 Jami gaplar: {len(KUNDALIK_GAPLAR)} ta"
    st[c] = st.get(c, {})
    st[c]["kundalik_gaplar"] = gaplar
    bot.send_message(c, txt, reply_markup=kundalik_menu())

def suhbat_korsat(c):
    x = st.get(c, {})
    kat = x.get("suhbat_kat")
    i = x.get("suhbat_i", 0)
    if not kat: return
    gaplar = SUHBAT_GAPLAR[kat]
    if i >= len(gaplar):
        x["suhbat_kat"] = None; st[c] = x
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    gap = gaplar[i]
    txt = f"💬 {kat} ({i+1}/{len(gaplar)})\n\n🇷🇺 {gap['ru']}\n\n🇺🇿 {gap['uz']}"
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    mk.add("🔊 Eshitish","⬅️ Oldingi","➡️ Keyingi")
    mk.add("⬅️ Orqaga")
    bot.send_message(c, txt, reply_markup=mk)

def next_savol(c):
    x = st.get(c, {})
    savol = random.choice(CHAT_SAVOLLAR)
    x["chat_savol"] = savol; x["chat"] = True; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⬅️ Orqaga")
    bot.send_message(c, f"💬 Chat\n\n{savol['savol']}\n\nRuscha javob yozing\n{savol['javob']}", reply_markup=mk)

def gap_tuzish(c):
    g = random.choice(GAPLAR)
    sozlar = g["sozlar"].copy(); random.shuffle(sozlar)
    st[c] = {"gap":True,"gap_togri":g["togri"],"tarj":False,"oyin":False,"a":False}
    txt = f"📝 Gap tuzish\n\nSo'zlardan gap tuzing:\n\n"
    for s in sozlar: txt += f"• {s}\n"
    txt += f"\n💡 {g['tarjima']}\n🎁 +15 ball"
    bot.send_message(c, txt, reply_markup=gap_menu())

def sovga(c):
    uid = str(c); bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D: D[uid] = {"oxirgi_kun":bugun,"streak":1,"challenge":False,"sovga":False}
    if D[uid].get("sovga"):
        bot.send_message(c, "Bugungi sovgani oldingiz!", reply_markup=menu()); return
    ball = random.choice([10,20,30,50,100])
    ball_qosh(c, ball)
    D[uid]["sovga"] = True; kunlik_saqlash()
    bot.send_message(c, f"🎁 Kunlik sovga!\n\nSizga +{ball} ball!\n🏆 Jami: {R.get(c,0)}", reply_markup=menu())

def talaffuz(c):
    if len(S) < 1: return
    s = random.choice(S)
    st[c] = {"talaffuz":s,"tarj":False,"oyin":False,"a":False}
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("🔊 Eshitish","👁 Tarjima","➡️ Keyingi so'z","⏹ To'xtatish")
    bot.send_message(c, f"🎵 Talaffuz\n\nRuscha: {s['ru']}\n\nEshitish", reply_markup=mk)

def yutuqlarim(c):
    uid = str(c); ball = R.get(uid, 0); streak = D.get(uid, {}).get("streak", 0)
    dostlar = len(F.get(uid, []))
    txt = "🏅 Yutuqlaringiz\n\n"
    if ball >= 1000: txt += "✅ 👑 Legenda (1000)\n"
    elif ball >= 500: txt += "✅ 🥇 Ustoz (500)\n"
    elif ball >= 100: txt += "✅ 🥈 Faol (100)\n"
    elif ball >= 10: txt += "✅ 🥉 Birinchi (10)\n"
    else: txt += "⏳ 🥉 Birinchi (10)\n"
    if streak >= 7: txt += "✅ 🔥 7 kun\n"
    else: txt += f"⏳ 🔥 7 kun ({streak}/7)\n"
    if dostlar >= 1: txt += "✅ 👥 Do'st\n"
    else: txt += "⏳ 👥 Do'st (0/1)\n"
    bot.send_message(c, txt)

def grafik(c):
    uid = str(c); ball = R.get(uid, 0)
    txt = "📊 Grafik\n\n"
    for d in [0, 100, 500, 1500, 3000, 5000]:
        if ball >= d: txt += f"✅ {d} ball\n"
        else: txt += f"⬜ {d} ball\n"
    txt += f"\n🏆 Siz: {ball}\n📊 {daraja(ball)}"
    bot.send_message(c, txt)

def sevimlilar(c):
    uid = str(c)
    if uid not in SV or not SV[uid]:
        bot.send_message(c, "⭐ Bosh. Flashcard da Saqlash bosing."); return
    txt = "⭐ Sevimlilar:\n\n"
    for i, rus in enumerate(SV[uid], 1):
        for s in S:
            if s["ru"] == rus: txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
    bot.send_message(c, txt)

def top10(c):
    if not R: bot.send_message(c, "🏆 Bosh."); return
    saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "🏆 TOP-10\n\n"
    medallar = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, (uid, ball) in enumerate(saralangan):
        ism = U.get(uid, {}).get("ism", "Nomalum")
        txt += f"{medallar[i]} {ism} — {ball}\n"
    bot.send_message(c, txt)

def mening_reyting(c):
    ball = R.get(str(c), 0)
    if not R: orin = 1
    else:
        saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)
        orin = 1
        for i, (uid, b) in enumerate(saralangan, 1):
            if uid == str(c): orin = i; break
    streak = D.get(c, {}).get("streak", 0)
    bot.send_message(c, f"📊 Reytingingiz\n\n🏆 Ball: {ball}\n📍 Orin: {orin} / {len(R)}\n📊 {daraja(ball)}\n🔥 Streak: {streak} kun")

def flash(c):
    x = st.get(c,{}); idx = x.get("i",0)
    if idx >= len(S):
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    s = S[idx]
    bot.send_message(c, f"Flashcard ({idx+1}/{len(S)})\n\nRuscha: {s['ru']}", reply_markup=flash_btn())

def test(c):
    x = st.get(c,{}); idx = x.get("ti",0)
    if idx >= len(S):
        sc = x.get("ts",0); tt = x.get("tt",0)
        x["ta"] = False; st[c] = x
        bot.send_message(c, f"Tugadi!\n\nJami: {tt}\nTogri: {sc}", reply_markup=menu()); return
    tg = S[idx]
    bs = [s for s in S if s["uz"] != tg["uz"]]
    if len(bs) < 3: bot.send_message(c, "Kam."); return
    nt = random.sample(bs, 3); vr = [tg] + nt; random.shuffle(vr)
    x["ca"] = tg["uz"]; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for v in vr: mk.add(v["uz"])
    mk.add("⏹ Testdan chiqish")
    bot.send_message(c, f"Test ({idx+1}/{len(S)})\n\n{tg['ru']} - ?", reply_markup=mk)

def oyin_navbat(c):
    x = st.get(c, {})
    if len(S) < 4:
        bot.send_message(c, "Kam.", reply_markup=menu()); return
    s = random.choice(S)
    x["oyin_javob"] = s["uz"]; x["oyin"] = True; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⏹ To'xtatish")
    bot.send_message(c, f"🎮 O'yin\n\nRuscha: {s['ru']}\n\nTarjima yozing\n🎁 +10 ball", reply_markup=mk)

def reklama_yubor():
    while True:
        time.sleep(3600)
        try:
            for uid in list(U.keys()):
                try:
                    bot.send_message(int(uid), REKLAMA_MATN, reply_markup=reklama_btn())
                    time.sleep(0.1)
                except: pass
        except: pass

Thread(target=reklama_yubor, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "Admin\n\n/royxat\n/talablar"); return
    if c in U and U[c].get("ism"):
        streak = kunlik_tekshir(m.chat.id)
        ball_qosh(m.chat.id, 1)
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, f"Salom, {U[c]['ism']}!\n\n📚 {len(S)} ta soz\n💬 {len(KUNDALIK_GAPLAR)} ta gap\n🔥 Streak: {streak} kun\n🏆 Ball: {R.get(c,0)}\n🎁 +1 ball!", reply_markup=menu())
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","sana_tugilgan":"","tel":"","h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, "Assalomu alaykum!\n\nIsmingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['royxat'])
def royxat(m):
    if m.chat.id != A: return
    txt = f"Foydalanuvchilar: {len(U)}\n\n"
    for uid, u in list(U.items())[:20]:
        txt += f"{u.get('ism','?')} {u.get('familiya','')} — {R.get(uid,0)} ball\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(commands=['talablar'])
def talablar_admin(m):
    if m.chat.id != A: return
    if not TT:
        bot.send_message(m.chat.id, "Talablar yoq."); return
    txt = f"Talablar: {len(TT)} ta\n\n"
    for i, (uid, talab) in enumerate(list(TT.items())[-20:], 1):
        ism = U.get(uid, {}).get("ism", "?")
        txt += f"{i}. {ism}:\n{talab['matn']}\n\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: str(m.chat.id) in U and U[str(m.chat.id)].get("h"))
def reg(m):
    c = str(m.chat.id); u = U[c]; t = m.text.strip()
    if u["h"] == "ism":
        if not ism_tekshir(t):
            bot.send_message(c, "Ism notogri!\nKamida 2 harf.\nQaytadan:"); return
        u["ism"] = t; u["h"] = "fam"; saqlash()
        bot.send_message(c, "Familiyangizni kiriting:")
    elif u["h"] == "fam":
        if not ism_tekshir(t):
            bot.send_message(c, "Familiya notogri!\nKamida 2 harf.\nQaytadan:"); return
        u["familiya"] = t; u["h"] = "sana"; saqlash()
        bot.send_message(c, "Tugilgan sana:\n\nFormat: DD.MM.YYYY")
    elif u["h"] == "sana":
        if not sana_tekshir(t):
            bot.send_message(c, "Sana notogri!\n\nFormat: DD.MM.YYYY\nMasalan: 15.05.1995\nQaytadan:"); return
        u["sana_tugilgan"] = t; u["h"] = "tel"; saqlash()
        bot.send_message(c, "Telefon:\n\nFormat: +XXXXXXXXXXXX")
    elif u["h"] == "tel":
        if not telefon_tekshir(t):
            bot.send_message(c, "Telefon notogri!\n\nMasalan: +998901234567\nQaytadan:"); return
        u["tel"] = t; u["h"] = ""; saqlash()
        ball_qosh(m.chat.id, 5); kunlik_tekshir(m.chat.id)
        bot.send_message(c, f"Rahmat, {u['ism']}!\n\n🎁 +5 ball!")
        bot.send_message(c, REKLAMA_MATN, reply_markup=reklama_btn())
        try: bot.send_message(A, f"YANGI:\n{u['ism']} {u['familiya']}\n{u['sana_tugilgan']}\n{u['tel']}")
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

    if x.get("kundalik_gaplar"):
        if t == "🔄 Yangilash": kundalik_gaplar(c); return
        if t == "🔊 Eshitish":
            for g in x.get("kundalik_gaplar", [])[:3]:
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={g['ru']}&tl=ru&client=tw-ob"
                    bot.send_voice(c, url); time.sleep(0.5)
                except: pass
            return
        if t == "⬅️ Orqaga":
            x["kundalik_gaplar"] = None; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return

    if x.get("talab"):
        if t == "⬅️ Orqaga":
            x["talab"] = False; x["talab_yozish"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "📢 Talab/taklif yozish":
            x["talab_yozish"] = True; st[c] = x
            bot.send_message(c, "Talab yoki taklifingizni yozing:"); return
        if t == "📋 Mening talablarim":
            bot.send_message(c, f"{TT.get(c, {}).get('matn', 'Yoq')}"); return
        if x.get("talab_yozish"):
            TT[c] = {"matn": t, "sana": datetime.now().strftime("%d.%m.%Y %H:%M")}
            talablar_saqlash()
            bot.send_message(c, "Rahmat!", reply_markup=menu())
            try: bot.send_message(A, f"YANGI:\n{U[c].get('ism','?')}:\n{t}")
            except: pass
            x["talab_yozish"] = False; x["talab"] = False; st[c] = x
            return
        return

    if x.get("suhbat_kat"):
        if t == "🔊 Eshitish":
            gap = SUHBAT_GAPLAR[x["suhbat_kat"]][x.get("suhbat_i",0)]["ru"]
            try:
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={gap}&tl=ru&client=tw-ob"
                bot.send_voice(c, url)
            except: pass
            return
        if t == "➡️ Keyingi": x["suhbat_i"] = x.get("suhbat_i",0)+1; st[c]=x; suhbat_korsat(c); return
        if t == "⬅️ Oldingi": x["suhbat_i"] = max(0,x.get("suhbat_i",0)-1); st[c]=x; suhbat_korsat(c); return
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

    if x.get("gap"):
        if t == "⏹ To'xtatish":
            x["gap"] = False; st[c] = x
            bot.send_message(c, "Toxtatildi.", reply_markup=menu()); return
        if t.strip().lower() == x.get("gap_togri","").lower():
            ball_qosh(m.chat.id, 15)
            bot.send_message(c, "Togri! +15 ball")
            x["gap"] = False; st[c] = x
            bot.send_message(c, "Yana oynash uchun Gap tuzish ni bosing.", reply_markup=menu())
        else: bot.send_message(c, f"Notogri. Togri: {x.get('gap_togri','')}")
        return

    if x.get("kat"):
        if t == "⬅️ Orqaga":
            x["kat"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in KATEGORIYALAR:
            txt = f"📚 {t}\n\n"
            for i, rus in enumerate(KATEGORIYALAR[t], 1):
                for s in S:
                    if s["ru"] == rus: txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
            bot.send_message(c, txt)
        return

    if x.get("gram"):
        if t == "⬅️ Orqaga":
            x["gram"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in GRAMMATIKA:
            bot.send_message(c, f"📖 {t}\n\n{GRAMMATIKA[t]}")
        return

    if x.get("dost"):
        if t == "⬅️ Orqaga":
            x["dost"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🔗 Havola":
            bot.send_message(c, f"Havolangiz:\n\nhttps://t.me/Til_organ_uz_bot?start={c}\n\n+50 ball!")
        elif t == "👥 Do'stlarim":
            dostlar = F.get(c, [])
            if not dostlar: bot.send_message(c, "Dostlaringiz yoq.")
            else:
                txt = "Dostlaringiz:\n\n"
                for i, d in enumerate(dostlar, 1):
                    txt += f"{i}. {U.get(d,{}).get('ism','?')} — {R.get(d,0)} ball\n"
                bot.send_message(c, txt)
        elif t == "🏆 Do'stlar reytingi":
            dostlar = F.get(c, [])
            if not dostlar: bot.send_message(c, "Dostlar yoq.")
            else:
                ballar = [(d, R.get(d,0)) for d in dostlar + [c]]
                ballar.sort(key=lambda x: x[1], reverse=True)
                txt = "Dostlar:\n\n"
                for i, (d, b) in enumerate(ballar, 1):
                    ism = U.get(d,{}).get("ism","?") if d != c else "Siz"
                    txt += f"{i}. {ism} — {b} ball\n"
                bot.send_message(c, txt)
        return

    if x.get("talaffuz"):
        if t == "⏹ To'xtatish":
            x["talaffuz"] = None; st[c] = x
            bot.send_message(c, "Toxtatildi.", reply_markup=menu()); return
        if t == "🔊 Eshitish":
            s = x.get("talaffuz")
            if s:
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={s['ru']}&tl=ru&client=tw-ob"
                    bot.send_voice(c, url)
                except: pass
        elif t == "👁 Tarjima":
            s = x.get("talaffuz")
            if s: bot.send_message(c, f"{s['ru']} — {s['uz']}")
        elif t == "➡️ Keyingi so'z": talaffuz(c)
        return

    if x.get("chat"):
        if t == "⬅️ Orqaga":
            x["chat"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if x.get("chat_savol"):
            if TARJIMA_BOR:
                try:
                    natija = GoogleTranslator(source='auto', target='ru').translate(t)
                    bot.send_message(c, f"RU: {natija}")
                except: pass
            next_savol(c)
        return

    if x.get("oyin"):
        if t == "⏹ To'xtatish":
            x["oyin"] = False; st[c] = x
            bot.send_message(c, "Toxtatildi.", reply_markup=menu()); return
        if x.get("oyin_javob"):
            togri = x["oyin_javob"]
            if t.lower().strip() == togri.lower().strip():
                ball_qosh(m.chat.id, 10)
                bot.send_message(c, "Togri! +10 ball")
                oyin_navbat(c)
            else:
                bot.send_message(c, f"Notogri. Togri: {togri}")
                oyin_navbat(c)
            return

    if x.get("tarj"):
        if t == "⬅️ Orqaga":
            x["tarj"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🇷🇺 Ruscha → 🇺🇿 O'zbekcha":
            x["tarj_til"] = "ru-uz"; st[c] = x
            bot.send_message(c, "Ruscha → Ozbekcha."); return
        if t == "🇺🇿 O'zbekcha → 🇷🇺 Ruscha":
            x["tarj_til"] = "uz-ru"; st[c] = x
            bot.send_message(c, "Ozbekcha → Ruscha."); return
        if TARJIMA_BOR:
            try:
                if x["tarj_til"] == "ru-uz":
                    natija = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"RU: {t}\n\nUZ: {natija}")
                else:
                    natija = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"UZ: {t}\n\nRU: {natija}")
            except: bot.send_message(c, "Tarjima xatosi.")
        return

    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; ball_qosh(m.chat.id, 5)
            bot.send_message(c, "Togri! +5 ball"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"Notogri. Togri: {x['ca']}"); test(c); return

    if t == "📅 Kundalik":
        ball_qosh(m.chat.id, 1)
        kundalik_gaplar(c)
    elif t == "📚 Flashcard":
        st[c] = {"i":0,"s":0,"t":0,"a":True,"tarj":False,"tarj_til":"ru-uz","oyin":False}; flash(c)
    elif t == "🎯 Testlar":
        st[c] = {"ti":0,"ts":0,"tt":0,"ta":True,"ca":None,"tarj":False,"oyin":False}; test(c)
    elif t == "🎮 O'yin":
        st[c] = {"oyin":True,"oyin_javob":None,"tarj":False,"a":False}; oyin_navbat(c)
    elif t == "💬 Suhbat":
        st[c] = {"suhbat":True}; bot.send_message(c, "Suhbat:", reply_markup=suhbat_menu())
    elif t == "📝 Gap tuzish":
        gap_tuzish(c)
    elif t == "📚 Kategoriya":
        st[c] = {"kat":True}; bot.send_message(c, "Kategoriya:", reply_markup=kategoriya_menu())
    elif t == "🎵 Talaffuz":
        talaffuz(c)
    elif t == "🎁 Sovga":
        sovga(c)
    elif t == "👥 Do'stlar":
        st[c] = {"dost":True}; bot.send_message(c, "Dostlar:", reply_markup=dost_menu())
    elif t == "⭐ Sevimlilar":
        sevimlilar(c)
    elif t == "📖 Grammatika":
        st[c] = {"gram":True}; bot.send_message(c, "Grammatika:", reply_markup=gram_menu())
    elif t == "💬 Chat":
        st[c] = {"chat":True}
        next_savol(c)
    elif t == "📢 Talab va taklif":
        st[c] = {"talab":True}; bot.send_message(c, "Talab:", reply_markup=talab_menu())
    elif t == "🏆 Reyting":
        bot.send_message(c, "Reyting:", reply_markup=reyting_menu())
    elif t == "🥇 TOP-10":
        top10(c)
    elif t == "📊 Mening reytingim":
        mening_reyting(c)
    elif t == "🏅 Yutuqlarim":
        yutuqlarim(c)
    elif t == "📊 Grafik statistika":
        grafik(c)
    elif t == "📊 Statistika":
        ball = R.get(c, 0); streak = D.get(c, {}).get("streak", 0)
        bot.send_message(c, f"Statistika\n\nJami: {len(S)}\nGaplar: {len(KUNDALIK_GAPLAR)}\nBall: {ball}\nDaraja: {daraja(ball)}\nStreak: {streak} kun")
    elif t == "ℹ️ Yordam":
        bot.send_message(c, "Yordam\n\nKundalik (+1)\nFlashcard (+2)\nTestlar (+5)\nO'yin (+10)\nGap tuzish (+15)\nDostlar (+50)\nSovga\nTalaffuz\nKategoriya\nGrammatika\nChat\nTalab va taklif\nSevimlilar\nReyting\nTarjima")
    elif t == "👁 Ko'rsatish":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]
            bot.send_message(c, f"Tarjima:\n\n{s['ru']} -> {s['uz']}", reply_markup=flash_btn())
    elif t == "🔊 Eshitish":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]
            try:
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={s['ru']}&tl=ru&client=tw-ob"
                bot.send_voice(c, url)
            except: pass
    elif t == "✅ Bilaman":
        ball_qosh(m.chat.id, 2)
        x["s"] = x.get("s",0)+1; x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "❌ Bilmayman":
        x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "⭐ Saqlash":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]; uid = str(c)
            if uid not in SV: SV[uid] = []
            if s["ru"] not in SV[uid]:
                SV[uid].append(s["ru"]); sevimlilar_saqlash()
                bot.send_message(c, "Saqlandi!")
            else: bot.send_message(c, "Allaqachon saqlangan.")
    elif t == "⏹ To'xtatish":
        x["a"] = False; st[c] = x
        bot.send_message(c, "Toxtatildi.", reply_markup=menu())
    elif t == "⏹ Testdan chiqish":
        x["ta"] = False; st[c] = x
        bot.send_message(c, "Toxtatildi.", reply_markup=menu())
    elif t == "⬅️ Orqaga":
        for k in ["ta","tarj","oyin","challenge","kat","dost","gap","gram","chat","talaffuz","suhbat","suhbat_kat","talab","kundalik_gaplar"]:
            x[k] = False
        st[c] = x
        bot.send_message(c, "Menyu:", reply_markup=menu())
    else:
        if TARJIMA_BOR and len(t) > 2:
            try:
                natija = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"Tarjima:\n\nRU: {t}\n\nUZ: {natija}")
                return
            except: pass
        bot.send_message(c, "Tugmalardan birini tanlang", reply_markup=menu())

print("Bot ishga tushdi...")
while True:
    try: bot.polling(non_stop=True, timeout=60)
    except Exception as e: print("Xato:", e); time.sleep(5)