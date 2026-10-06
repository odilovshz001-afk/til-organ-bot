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

import telebot, random, json, time
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
U, R, D, F, SV, TUR = {}, {}, {}, {}, {}, {}
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

for fname in ["users.json","reyting.json","kunlik.json","dostlar.json","sevimlilar.json","turnir.json"]:
    if os.path.exists(fname):
        try:
            data = json.load(open(fname, encoding="utf-8"))
            if fname == "users.json": U = data
            elif fname == "reyting.json": R = data
            elif fname == "kunlik.json": D = data
            elif fname == "dostlar.json": F = data
            elif fname == "sevimlilar.json": SV = data
            elif fname == "turnir.json": TUR = data
        except: pass

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
    {"togri":"Спасибо большое","sozlar":["большое","Спасибо"],"tarjima":"Katta rahmat"},
    {"togri":"Доброе утро","sozlar":["утро","Доброе"],"tarjima":"Xayrli tong"},
    {"togri":"Я иду домой","sozlar":["домой","иду","Я"],"tarjima":"Men uyga ketyapman"}
]

GRAMMATIKA = {
    "📘 Fe'l zamonlari": "Настоящее время:\n• Я читаю (Men o'qiyapman)\n• Ты читаешь\n• Он читает\n\nПрошедшее:\n• Я читал\n• Ты читал\n\nБудущее:\n• Я буду читать",
    "📗 Kelishiklar": "Именительный: стол (stol)\nРодительный: стола (stolning)\nДательный: столу (stolga)\nВинительный: стол (stolni)\nТворительный: столом (stol bilan)\nПредложный: о столе (stol haqida)",
    "📙 Sonlar": "1 один — bir\n2 два — ikki\n3 три — uch\n4 четыре — to'rt\n5 пять — besh\n6 шесть — olti\n7 семь — yetti\n8 восемь — sakkiz\n9 девять — to'qqiz\n10 десять — o'n",
    "📕 Ranglar": "красный — qizil\nсиний — ko'k\nзелёный — yashil\nжёлтый — sariq\nчёрный — qora\nбелый — oq\nоранжевый — to'q sariq"
}

CHAT_SAVOLLAR = [
    {"savol":"Как тебя зовут?","javob":"Меня зовут..."},
    {"savol":"Откуда ты?","javob":"Я из Узбекистана"},
    {"savol":"Сколько тебе лет?","javob":"Мне ... лет"},
    {"savol":"Что ты любишь?","javob":"Я люблю..."},
    {"savol":"Где ты живёшь?","javob":"Я живу в..."}
]

print(f"JAMI: {len(S)} ta so'z")

st = {}

def saqlash(): json.dump(U, open("users.json","w",encoding="utf-8"), ensure_ascii=False)
def reyting_saqlash(): json.dump(R, open("reyting.json","w",encoding="utf-8"), ensure_ascii=False)
def kunlik_saqlash(): json.dump(D, open("kunlik.json","w",encoding="utf-8"), ensure_ascii=False)
def dostlar_saqlash(): json.dump(F, open("dostlar.json","w",encoding="utf-8"), ensure_ascii=False)
def sevimlilar_saqlash(): json.dump(SV, open("sevimlilar.json","w",encoding="utf-8"), ensure_ascii=False)
def turnir_saqlash(): json.dump(TUR, open("turnir.json","w",encoding="utf-8"), ensure_ascii=False)

def ball_qosh(user_id, ball):
    uid = str(user_id)
    R[uid] = R.get(uid, 0) + ball
    reyting_saqlash()

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
    m.add("📝 Gap tuzish","📚 Kategoriya","🎵 Talaffuz","🎁 Sovga")
    m.add("👥 Do'stlar","⭐ Sevimlilar","🏆 Reyting","📖 Grammatika")
    m.add("💬 Chat","📊 Statistika","🔄 Tarjima","ℹ️ Yordam")
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
    m.add("📊 Grafik statistika","🏆 Haftalik turnir","⬅️ Orqaga")
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

def reja_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("🎯 10 so'z/kun","🎯 30 daqiqa/kun","📊 Rejam holati","⬅️ Orqaga")
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

def haftalik_tekshir():
    while True:
        try:
            hozir = datetime.now()
            if hozir.weekday() == 0 and hozir.hour == 9:
                if TUR.get("hafta") != hozir.strftime("%Y-%W"):
                    TUR["hafta"] = hozir.strftime("%Y-%W")
                    turnir_saqlash()
                    saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)[:3]
                    for i, (uid, ball) in enumerate(saralangan):
                        bonus = [100, 50, 25][i]
                        ball_qosh(uid, bonus)
                        try: bot.send_message(int(uid), f"🏆 Haftalik turnir! Siz {i+1}-o'rinda! +{bonus} ball!")
                        except: pass
            time.sleep(3600)
        except: time.sleep(3600)

Thread(target=haftalik_tekshir, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "Admin\n\n/royxat"); return
    if len(m.text.split()) > 1:
        try:
            taklif = m.text.split()[1]
            if taklif in U and taklif != c:
                if c not in F: F[c] = []
                if taklif not in F: F[taklif] = []
                if c not in F[taklif]: F[taklif].append(c)
                if taklif not in F[c]: F[c].append(taklif)
                dostlar_saqlash()
                ball_qosh(c, 50); ball_qosh(taklif, 50)
                try: bot.send_message(int(taklif), f"🎉 Yangi do'st! +50 ball")
                except: pass
        except: pass
    if c in U and U[c].get("ism"):
        streak = kunlik_tekshir(m.chat.id)
        ball_qosh(m.chat.id, 1)
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, f"Salom, {U[c]['ism']}! 👋\n\n📚 {len(S)} ta so'z\n🔥 Streak: {streak} kun\n🏆 Ball: {R.get(c,0)}\n🎁 +1 ball!", reply_markup=menu())
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","tel":"","h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, "Assalomu alaykum!\n\nIsmingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['royxat'])
def royxat(m):
    if m.chat.id != A: return
    txt = f"👥 Foydalanuvchilar: {len(U)}\n\n"
    for uid, u in list(U.items())[:20]:
        txt += f"• {u.get('ism','?')} — {R.get(uid,0)} ball\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: str(m.chat.id) in U and U[str(m.chat.id)].get("h"))
def reg(m):
    c = str(m.chat.id); u = U[c]; t = m.text.strip()
    if u["h"] == "ism":
        u["ism"] = t; u["h"] = "fam"; saqlash()
        bot.send_message(c, "Familiyangizni kiriting:")
    elif u["h"] == "fam":
        u["familiya"] = t; u["h"] = "tel"; saqlash()
        bot.send_message(c, "Telefon raqamingizni kiriting:")
    elif u["h"] == "tel":
        u["tel"] = t; u["h"] = ""; saqlash()
        ball_qosh(m.chat.id, 5); kunlik_tekshir(m.chat.id)
        bot.send_message(c, f"Rahmat, {u['ism']}! 🎉\n📚 {len(S)} ta so'z.\n🎁 +5 ball!")
        try: bot.send_message(A, f"YANGI:\n{u['ism']} {u['familiya']}\n{u['tel']}")
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

    # GAP
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

    # REJA
    if x.get("reja"):
        if t == "⬅️ Orqaga":
            x["reja"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🎯 10 so'z/kun":
            if c not in D: D[c] = {"oxirgi_kun":"","streak":0,"challenge":False,"sovga":False}
            D[c]["reja"] = 10; kunlik_saqlash()
            bot.send_message(c, "✅ Reja: 10 so'z/kun")
        elif t == "🎯 30 daqiqa/kun":
            if c not in D: D[c] = {"oxirgi_kun":"","streak":0,"challenge":False,"sovga":False}
            D[c]["reja"] = 30; kunlik_saqlash()
            bot.send_message(c, "✅ Reja: 30 daqiqa/kun")
        elif t == "📊 Rejam holati":
            reja = D.get(c, {}).get("reja", 0)
            if reja == 10: bot.send_message(c, "📊 Reja: 10 so'z/kun\nKo'rilgan: 0")
            elif reja == 30: bot.send_message(c, "📊 Reja: 30 daqiqa/kun")
            else: bot.send_message(c, "Reja qo'yilmagan.")
        return

    # DO'STLAR
    if x.get("dost"):
        if t == "⬅️ Orqaga":
            x["dost"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🔗 Havola":
            link = f"https://t.me/Til_organ_uz_bot?start={c}"
            bot.send_message(c, f"🔗 *Havolangiz:*\n\n`{link}`\n\nDo'stingizga yuboring. +50 ball!", parse_mode='Markdown')
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
                txt = "🏆 *Do'stlar reytingi:*\n\n"
                for i, (d, b) in enumerate(ballar, 1):
                    ism = U.get(d,{}).get("ism","?") if d != c else "Siz"
                    txt += f"{i}. {ism} — {b} ball\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        return

    # TALAFFUZ
    if x.get("talaffuz"):
        if t == "⏹ To'xtatish":
            x["talaffuz"] = None; st[c] = x
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if t == "🔊 Eshitish":
            s = x.get("talaffuz")
            if s:
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={s['ru']}&tl=ru&client=tw-ob"
                    bot.send_voice(c, url)
                except: bot.send_message(c, "❌ Audio xato")
        elif t == "👁 Tarjima":
            s = x.get("talaffuz")
            if s: bot.send_message(c, f"{s['ru']} — {s['uz']}")
        elif t == "➡️ Keyingi so'z":
            talaffuz(c)
        return

    # CHAT
    if x.get("chat"):
        if t == "⬅️ Orqaga":
            x["chat"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        savol = x.get("chat_savol")
        if savol:
            if TARJIMA_BOR:
                try:
                    natija = GoogleTranslator(source='auto', target='ru').translate(t)
                    bot.send_message(c, f"🇷🇺 {natija}\n\n_(Sizning javobingiz ruscha)_", parse_mode='Markdown')
                except: pass
            next_savol(c)
        return

    # O'YIN
    if x.get("oyin"):
        if t == "⏹ To'xtatish":
            x["oyin"] = False; st[c] = x
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if x.get("oyin_javob"):
            togri = x["oyin_javob"]
            if t.lower().strip() == togri.lower().strip():
                ball_qosh(m.chat.id, 10)
                bot.send_message(c, f"✅ To'g'ri! +10 ball\n🏆 Jami: {R.get(c,0)}")
                oyin_navbat(c)
            else:
                bot.send_message(c, f"❌ Noto'g'ri. To'g'ri: {togri}")
                oyin_navbat(c)
            return

    # CHALLENGE
    if x.get("challenge"):
        if t == "⏹ To'xtatish":
            x["challenge"] = False; st[c] = x
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if x.get("javob"):
            togri = x["javob"]
            if t.lower().strip() == togri.lower().strip():
                ball_qosh(m.chat.id, 20)
                if c in D: D[c]["challenge"] = True; kunlik_saqlash()
                x["javob"] = None; x["challenge"] = False; st[c] = x
                bot.send_message(c, f"✅ To'g'ri! +20 ball 🎁\n🏆 Jami: {R.get(c,0)}", reply_markup=menu())
            else:
                x["javob"] = None; x["challenge"] = False; st[c] = x
                bot.send_message(c, f"❌ Noto'g'ri. To'g'ri: {togri}", reply_markup=menu())
            return

    # TARJIMA
    if x.get("tarj"):
        if t == "⬅️ Orqaga":
            x["tarj"] = False; st[c] = x
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🇷🇺 Ruscha → 🇺🇿 O'zbekcha":
            x["tarj_til"] = "ru-uz"; st[c] = x
            bot.send_message(c, "✅ Ruscha → O'zbekcha."); return
        if t == "🇺🇿 O'zbekcha → 🇷🇺 Ruscha":
            x["tarj_til"] = "uz-ru"; st[c] = x
            bot.send_message(c, "✅ O'zbekcha → Ruscha."); return
        if TARJIMA_BOR:
            try:
                if x["tarj_til"] == "ru-uz":
                    natija = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"🇷🇺 {t}\n\n🇺🇿 {natija}")
                else:
                    natija = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"🇺🇿 {t}\n\n🇷🇺 {natija}")
            except: bot.send_message(c, "❌ Tarjima xatosi.")
        return

    # TEST
    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; ball_qosh(m.chat.id, 5)
            bot.send_message(c, "✅ Togri! +5 ball"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"❌ Notogri. Togri: {x['ca']}"); test(c); return

    # MENYU
    if t == "📅 Kundalik":
        ball_qosh(m.chat.id, 1)
        k = datetime.now().day; gs = 10; jg = max(1, len(S)//gs); gi = k % jg
        sz = S[gi*gs:(gi+1)*gs]
        txt = f"📅 Kundalik - {datetime.now().strftime('%d.%m.%Y')}\n\n"
        for i, s in enumerate(sz, 1): txt += f"{i}. {s['ru']} - {s['uz']}\n\n"
        txt += f"🎁 +1 ball\n🏆 Jami: {R.get(c,0)}"
        bot.send_message(c, txt)
    elif t == "📚 Flashcard":
        st[c] = {"i":0,"s":0,"t":0,"a":True,"tarj":False,"tarj_til":"ru-uz","oyin":False}; flash(c)
    elif t == "🎯 Testlar":
        st[c] = {"ti":0,"ts":0,"tt":0,"ta":True,"ca":None,"tarj":False,"oyin":False}; test(c)
    elif t == "🎮 O'yin":
        st[c] = {"oyin":True,"oyin_javob":None,"tarj":False,"a":False}; oyin_navbat(c)
    elif t == "📝 Gap tuzish":
        gap_tuzish(c)
    elif t == "📚 Kategoriya":
        st[c] = {"kat":True}; bot.send_message(c, "📚 Kategoriya:", reply_markup=kategoriya_menu())
    elif t == "🎵 Talaffuz":
        talaffuz(c)
    elif t == "🎁 Sovga":
        sovga(c)
    elif t == "👥 Do'stlar":
        st[c] = {"dost":True}; bot.send_message(c, "👥 Do'stlar:", reply_markup=dost_menu())
    elif t == "⭐ Sevimlilar":
        sevimlilar(c)
    elif t == "📖 Grammatika":
        st[c] = {"gram":True}; bot.send_message(c, "📖 Grammatika:", reply_markup=gram_menu())
    elif t == "💬 Chat":
        st[c] = {"chat":True}
        next_savol(c)
    elif t == "🏆 Reyting":
        bot.send_message(c, "🏆 Reyting:", reply_markup=reyting_menu())
    elif t == "🥇 TOP-10":
        top10(c)
    elif t == "📊 Mening reytingim":
        mening_reyting(c)
    elif t == "🏅 Yutuqlarim":
        yutuqlarim(c)
    elif t == "📊 Grafik statistika":
        grafik(c)
    elif t == "🏆 Haftalik turnir":
        if TUR.get("hafta"):
            bot.send_message(c, f"🏆 Haftalik turnir\n\nHafta: {TUR['hafta']}\nTOP-3 ga bonus: 100/50/25")
        else: bot.send_message(c, "🏆 Turnir hali boshlanmagan.")
    elif t == "📊 Statistika":
        ball = R.get(c, 0); streak = D.get(c, {}).get("streak", 0)
        bot.send_message(c, f"📊 *Statistika*\n\n📚 Jami: {len(S)}\n📖 Ko'rilgan: {x.get('i',0)}\n✅ To'g'ri: {x.get('s',0)}\n\n🏆 Ball: {ball}\n📊 Daraja: {daraja(ball)}\n🔥 Streak: {streak} kun", parse_mode='Markdown')
    elif t == "ℹ️ Yordam":
        bot.send_message(c, "📖 Yordam\n\n📅 Kundalik (+1)\n📚 Flashcard (+2)\n🎯 Testlar (+5)\n🎮 O'yin (+10)\n📝 Gap tuzish (+15)\n🎁 Challenge (+20)\n👥 Do'stlar (+50)\n🎁 Sovga (random)\n🎵 Talaffuz\n📚 Kategoriya\n📖 Grammatika\n💬 Chat\n⭐ Sevimlilar\n🏆 Reyting\n🔄 Tarjima")
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
            except: bot.send_message(c, "❌ Audio xato")
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
                bot.send_message(c, "⭐ Saqlandi!")
            else: bot.send_message(c, "Allaqachon saqlangan.")
    elif t == "⏹ To'xtatish":
        x["a"] = False; st[c] = x
        bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⏹ Testdan chiqish":
        x["ta"] = False; st[c] = x
        bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⬅️ Oldingi":
        sh = x.get("sh",0)-1
        if sh < 0: bot.send_message(c, "Birinchi sahifa.")
        else: barcha(c, sh)
    elif t == "➡️ Keyingi":
        sh = x.get("sh",0)+1
        js = (len(S)+19)//20
        if sh >= js: bot.send_message(c, "Oxirgi sahifa.")
        else: barcha(c, sh)
    elif t == "⬅️ Orqaga":
        for k in ["ta","tarj","oyin","challenge","kat","dost","gap","gram","chat","talaffuz","reja"]:
            x[k] = False
        st[c] = x
        bot.send_message(c, "Menyu:", reply_markup=menu())
    else:
        if TARJIMA_BOR and len(t) > 2:
            try:
                natija = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"📝 Tarjima:\n\n🇷🇺 {t}\n\n🇺🇿 {natija}")
                return
            except: pass
        bot.send_message(c, "Tugmalardan birini tanlang", reply_markup=menu())

def next_savol(c):
    x = st.get(c, {})
    savol = random.choice(CHAT_SAVOLLAR)
    x["chat_savol"] = savol
    x["chat"] = True
    st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⬅️ Orqaga")
    bot.send_message(c, f"💬 *Chat*\n\n{savol['savol']}\n\n_(Ruscha javob yozing)_\n\n💡 Namuna: {savol['javob']}", parse_mode='Markdown', reply_markup=mk)

def gap_tuzish(c):
    g = random.choice(GAPLAR)
    sozlar = g["sozlar"].copy(); random.shuffle(sozlar)
    st[c] = {"gap":True,"gap_togri":g["togri"],"tarj":False,"oyin":False,"a":False}
    txt = f"📝 *Gap tuzish*\n\nSo'zlardan gap tuzing:\n\n"
    for s in sozlar: txt += f"• {s}\n"
    txt += f"\n💡 _{g['tarjima']}_\n🎁 +15 ball"
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=gap_menu())

def sovga(c):
    uid = str(c); bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D: D[uid] = {"oxirgi_kun":bugun,"streak":1,"challenge":False,"sovga":False}
    if D[uid].get("sovga"):
        bot.send_message(c, "✅ Bugungi sovgani oldingiz!", reply_markup=menu()); return
    ball = random.choice([10,20,30,50,100])
    ball_qosh(c, ball)
    D[uid]["sovga"] = True; kunlik_saqlash()
    bot.send_message(c, f"🎁 *Kunlik sovga!*\n\nSizga *+{ball} ball*!\n🏆 Jami: {R.get(c,0)}", parse_mode='Markdown', reply_markup=menu())

def talaffuz(c):
    if len(S) < 1: return
    s = random.choice(S)
    st[c] = {"talaffuz":s,"tarj":False,"oyin":False,"a":False}
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("🔊 Eshitish","👁 Tarjima","➡️ Keyingi so'z","⏹ To'xtatish")
    bot.send_message(c, f"🎵 *Talaffuz*\n\nRuscha: *{s['ru']}*\n\n«🔊 Eshitish»", parse_mode='Markdown', reply_markup=mk)

def yutuqlarim(c):
    uid = str(c); ball = R.get(uid, 0); streak = D.get(uid, {}).get("streak", 0)
    dostlar = len(F.get(uid, []))
    txt = "🏅 *Yutuqlaringiz*\n\n"
    if ball >= 1000: txt += "✅ 👑 Legenda (1000)\n"
    elif ball >= 500: txt += "✅ 🥇 Ustoz (500)\n"
    elif ball >= 100: txt += "✅ 🥈 Faol (100)\n"
    elif ball >= 10: txt += "✅ 🥉 Birinchi (10)\n"
    else: txt += "⏳ 🥉 Birinchi (10)\n"
    if streak >= 7: txt += "✅ 🔥 7 kun\n"
    else: txt += f"⏳ 🔥 7 kun ({streak}/7)\n"
    if dostlar >= 1: txt += "✅ 👥 Do'st (1)\n"
    else: txt += "⏳ 👥 Do'st (0/1)\n"
    bot.send_message(c, txt, parse_mode='Markdown')

def grafik(c):
    uid = str(c); ball = R.get(uid, 0)
    darajalar = [0, 100, 500, 1500, 3000, 5000]
    txt = "📊 *Grafik statistika*\n\n"
    for d in darajalar:
        if ball >= d:
            txt += f"✅ {d} ball\n"
        else:
            txt += f"⬜ {d} ball\n"
    txt += f"\n🏆 Siz: {ball} ball\n📊 Daraja: {daraja(ball)}"
    bot.send_message(c, txt, parse_mode='Markdown')

def sevimlilar(c):
    uid = str(c)
    if uid not in SV or not SV[uid]:
        bot.send_message(c, "⭐ Bo'sh. Flashcard da «⭐ Saqlash» bosing."); return
    txt = "⭐ *Sevimlilar:*\n\n"
    for i, rus in enumerate(SV[uid], 1):
        for s in S:
            if s["ru"] == rus:
                txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
    bot.send_message(c, txt, parse_mode='Markdown')

def top10(c):
    if not R: bot.send_message(c, "🏆 Bo'sh."); return
    saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "🏆 *TOP-10*\n\n"
    medallar = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, (uid, ball) in enumerate(saralangan):
        ism = U.get(uid, {}).get("ism", "Noma'lum")
        txt += f"{medallar[i]} {ism} — {ball}\n"
    bot.send_message(c, txt, parse_mode='Markdown')

def mening_reyting(c):
    ball = R.get(str(c), 0)
    if not R: orin = 1
    else:
        saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)
        orin = 1
        for i, (uid, b) in enumerate(saralangan, 1):
            if uid == str(c): orin = i; break
    streak = D.get(c, {}).get("streak", 0)
    bot.send_message(c, f"📊 *Reytingingiz*\n\n🏆 Ball: *{ball}*\n📍 O'rin: *{orin}* / {len(R)}\n📊 Daraja: {daraja(ball)}\n🔥 Streak: {streak} kun", parse_mode='Markdown')

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

def barcha(c, sh=0):
    ss = 20; j = len(S); js = (j+ss-1)//ss
    if sh < 0: sh = 0
    if sh >= js: sh = js-1
    sz = S[sh*ss:(sh+1)*ss]
    txt = f"Barcha - {sh+1}/{js}\n\n"
    for i, s in enumerate(sz, sh*ss+1):
        txt += f"{i}. {s['ru']} - {s['uz']}\n"
    x = st.get(c,{}); x["sh"] = sh; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("⬅️ Oldingi","➡️ Keyingi","⬅️ Orqaga")
    bot.send_message(c, txt, reply_markup=mk)

print("Bot ishga tushdi...")
while True:
    try: bot.polling(non_stop=True, timeout=60)
    except Exception as e: print("Xato:", e); time.sleep(5)