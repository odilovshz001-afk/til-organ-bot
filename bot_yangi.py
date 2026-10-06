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
from datetime import datetime

# Tarjima kutubxonasi
try:
    from deep_translator import GoogleTranslator
    TARJIMA_BOR = True
except:
    TARJIMA_BOR = False
    print("⚠️ deep-translator yo'q — tarjima ishlamaydi")

T = "8774189119:AAGM1_wXOJ_pGwkyYKSIdgkOSWPVoudTn6M"
A = 8178917212

REKLAMA = "\n\n━━━━━━━━━━━━━━━━\n📸 Instagram: @odilov03_\n💬 Telegram: @odilov0_3"

def insta_btn():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("📸 Instagram", url="https://instagram.com/odilov03_"),
        types.InlineKeyboardButton("💬 Telegram", url="https://t.me/odilov0_3")
    )
    return m

bot = telebot.TeleBot(T)
U = {}
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

if os.path.exists("users.json"):
    try: U = json.load(open("users.json", encoding="utf-8"))
    except: pass

print(f"JAMI: {len(S)} ta so'z")

st = {}

def saqlash():
    json.dump(U, open("users.json","w",encoding="utf-8"), ensure_ascii=False)

def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📅 Kundalik","📚 Flashcard","🎯 Testlar","📖 Barcha","🔄 Tarjima","📊 Statistika","ℹ️ Yordam")
    return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish","✅ Bilaman","❌ Bilmayman","⏹ To'xtatish")
    return m

def tarjima_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇷🇺 Ruscha → 🇺🇿 O'zbekcha","🇺🇿 O'zbekcha → 🇷🇺 Ruscha","⬅️ Orqaga")
    return m

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "Admin"); return
    if c in U and U[c].get("ism"):
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz"}
        bot.send_message(c, f"Salom, {U[c]['ism']}!\n\n{len(S)} ta so'z mavjud.{REKLAMA}", reply_markup=menu())
        bot.send_message(c, "Bizni kuzatib boring 👇", reply_markup=insta_btn())
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","tel":"","h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, f"Assalomu alaykum!\n\nIsmingizni kiriting:{REKLAMA}", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: str(m.chat.id) in U and U[str(m.chat.id)].get("h"))
def reg(m):
    c = str(m.chat.id); u = U[c]; t = m.text.strip()
    if u["h"] == "ism":
        u["ism"] = t; u["h"] = "fam"; saqlash()
        bot.send_message(c, f"Familiyangizni kiriting:{REKLAMA}")
    elif u["h"] == "fam":
        u["familiya"] = t; u["h"] = "tel"; saqlash()
        bot.send_message(c, f"Telefon raqamingizni kiriting:{REKLAMA}")
    elif u["h"] == "tel":
        u["tel"] = t; u["h"] = ""; saqlash()
        bot.send_message(c, f"Rahmat, {u['ism']}!\n\n{len(S)} ta so'z mavjud.{REKLAMA}")
        try: bot.send_message(A, f"YANGI:\n{u['ism']} {u['familiya']}\n{u['tel']}")
        except: pass
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz"}
        bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
        bot.send_message(c, "Bizni kuzatib boring 👇", reply_markup=insta_btn())

@bot.message_handler(func=lambda m: True)
def hand(m):
    c = str(m.chat.id); t = m.text
    if m.chat.id == A: return
    if c not in U or not U[c].get("ism") or U[c].get("h"): return
    if c not in st: st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz"}
    x = st[c]

    # ===== TARJIMA REJIMI =====
    if x.get("tarj"):
        if t == "⬅️ Orqaga":
            x["tarj"] = False; st[c] = x
            bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
            return
        if t == "🇷🇺 Ruscha → 🇺🇿 O'zbekcha":
            x["tarj_til"] = "ru-uz"; st[c] = x
            bot.send_message(c, f"✅ Ruscha → O'zbekcha rejimi.\n\nEndi ruscha so'z yoki gap yozing.{REKLAMA}")
            return
        if t == "🇺🇿 O'zbekcha → 🇷🇺 Ruscha":
            x["tarj_til"] = "uz-ru"; st[c] = x
            bot.send_message(c, f"✅ O'zbekcha → Ruscha rejimi.\n\nEndi o'zbekcha so'z yoki gap yozing.{REKLAMA}")
            return
        # Tarjima qilamiz
        if TARJIMA_BOR:
            try:
                if x["tarj_til"] == "ru-uz":
                    natija = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"🇷🇺 {t}\n\n🇺🇿 {natija}{REKLAMA}")
                else:
                    natija = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"🇺🇿 {t}\n\n🇷🇺 {natija}{REKLAMA}")
            except Exception as e:
                bot.send_message(c, f"❌ Tarjima xatosi: {e}{REKLAMA}")
        else:
            bot.send_message(c, f"❌ Tarjima xizmati ishlamayapti.{REKLAMA}")
        return

    # ===== TEST JAVOBI =====
    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"Togri!{REKLAMA}"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"Notogri. Togri: {x['ca']}{REKLAMA}"); test(c); return

    # ===== MENYU =====
    if t == "📅 Kundalik":
        k = datetime.now().day; gs = 10; jg = max(1, len(S)//gs); gi = k % jg
        sz = S[gi*gs:(gi+1)*gs]
        txt = f"Kundalik - {datetime.now().strftime('%d.%m.%Y')}\n\n"
        for i, s in enumerate(sz, 1): txt += f"{i}. {s['ru']} - {s['uz']}\n\n"
        bot.send_message(c, txt + REKLAMA)
    elif t == "📚 Flashcard":
        st[c] = {"i":0,"s":0,"t":0,"a":True,"tarj":False,"tarj_til":"ru-uz"}; flash(c)
    elif t == "🎯 Testlar":
        st[c] = {"ti":0,"ts":0,"tt":0,"ta":True,"ca":None,"tarj":False}; test(c)
    elif t == "📖 Barcha":
        barcha(c, 0)
    elif t == "🔄 Tarjima":
        x["tarj"] = True; st[c] = x
        bot.send_message(c, f"🔄 Tarjima rejimi.\n\nYo'nalishni tanlang:{REKLAMA}", reply_markup=tarjima_menu())
    elif t == "📊 Statistika":
        bot.send_message(c, f"Jami: {len(S)}\nKorilgan: {x.get('i',0)}\nTogri: {x.get('s',0)}{REKLAMA}")
    elif t == "ℹ️ Yordam":
        bot.send_message(c, f"📖 Yordam\n\n• 📅 Kundalik — kunlik so'zlar\n• 📚 Flashcard — so'z yodlash\n• 🎯 Testlar — bilim sinash\n• 📖 Barcha — hamma so'zlar\n• 🔄 Tarjima — matn tarjimasi{REKLAMA}")
    elif t == "👁 Ko'rsatish":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]
            bot.send_message(c, f"Tarjima:\n\n{s['ru']} -> {s['uz']}{REKLAMA}", reply_markup=flash_btn())
    elif t == "✅ Bilaman":
        x["s"] = x.get("s",0)+1; x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "❌ Bilmayman":
        x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "⏹ To'xtatish":
        x["a"] = False; st[c] = x
        bot.send_message(c, f"To'xtatildi.{REKLAMA}", reply_markup=menu())
    elif t == "⏹ Testdan chiqish":
        x["ta"] = False; st[c] = x
        bot.send_message(c, f"To'xtatildi.{REKLAMA}", reply_markup=menu())
    elif t == "⬅️ Oldingi":
        sh = x.get("sh",0)-1
        if sh < 0: bot.send_message(c, f"Birinchi sahifa.{REKLAMA}")
        else: barcha(c, sh)
    elif t == "➡️ Keyingi":
        sh = x.get("sh",0)+1
        js = (len(S)+19)//20
        if sh >= js: bot.send_message(c, f"Oxirgi sahifa.{REKLAMA}")
        else: barcha(c, sh)
    elif t == "⬅️ Orqaga":
        x["ta"] = False; x["tarj"] = False; st[c] = x
        bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
    else:
        # Agar foydalanuvchi menuda bo'lmasa va matn yozsa
        if TARJIMA_BOR and len(t) > 2:
            try:
                natija = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"📝 Tarjima:\n\n🇷🇺 {t}\n\n🇺🇿 {natija}{REKLAMA}")
                return
            except: pass
        bot.send_message(c, f"Tugmalardan birini tanlang{REKLAMA}", reply_markup=menu())

def flash(c):
    x = st.get(c,{}); idx = x.get("i",0)
    if idx >= len(S):
        bot.send_message(c, f"Tugadi!{REKLAMA}", reply_markup=menu()); return
    s = S[idx]
    bot.send_message(c, f"Flashcard ({idx+1}/{len(S)})\n\nRuscha: {s['ru']}{REKLAMA}", reply_markup=flash_btn())

def test(c):
    x = st.get(c,{}); idx = x.get("ti",0)
    if idx >= len(S):
        sc = x.get("ts",0); tt = x.get("tt",0)
        x["ta"] = False; st[c] = x
        bot.send_message(c, f"Tugadi!\n\nJami: {tt}\nTogri: {sc}{REKLAMA}", reply_markup=menu()); return
    tg = S[idx]
    bs = [s for s in S if s["uz"] != tg["uz"]]
    if len(bs) < 3: bot.send_message(c, f"So'zlar kam.{REKLAMA}"); return
    nt = random.sample(bs, 3)
    vr = [tg] + nt
    random.shuffle(vr)
    x["ca"] = tg["uz"]; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for v in vr: mk.add(v["uz"])
    mk.add("⏹ Testdan chiqish")
    bot.send_message(c, f"Test ({idx+1}/{len(S)})\n\n{tg['ru']} - ?{REKLAMA}", reply_markup=mk)

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
    bot.send_message(c, txt + REKLAMA, reply_markup=mk)

print("Bot ishga tushdi...")
while True:
    try: bot.polling(non_stop=True, timeout=60)
    except Exception as e: print("Xato:", e); time.sleep(5)