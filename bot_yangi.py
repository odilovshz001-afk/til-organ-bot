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

T = "8774189119:AAGM1_wXOJ_pGwkyYKSIdgkOSWPVoudTn6M"
A = 8178917212

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
    m.add("📅 Kundalik","📚 Flashcard","🎯 Testlar","📖 Barcha","📊 Statistika","ℹ️ Yordam")
    return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish","✅ Bilaman","❌ Bilmayman","⏹ To'xtatish")
    return m

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "Admin"); return
    if c in U and U[c].get("ism"):
        st[c] = {"i":0,"s":0,"t":0,"a":False}
        bot.send_message(c, f"Salom, {U[c]['ism']}!\n\n{len(S)} ta so'z.", reply_markup=menu())
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","tel":"","h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, "Assalomu alaykum!\n\nIsmingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

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
        bot.send_message(c, f"Rahmat, {u['ism']}!\n\n{len(S)} ta so'z mavjud.")
        try: bot.send_message(A, f"YANGI:\n{u['ism']} {u['familiya']}\n{u['tel']}")
        except: pass
        st[c] = {"i":0,"s":0,"t":0,"a":False}
        bot.send_message(c, "Menyu:", reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def hand(m):
    c = str(m.chat.id); t = m.text
    if m.chat.id == A: return
    if c not in U or not U[c].get("ism") or U[c].get("h"): return
    if c not in st: st[c] = {"i":0,"s":0,"t":0,"a":False}
    x = st[c]

    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, "Togri!"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"Notogri. Togri: {x['ca']}"); test(c); return

    if t == "📅 Kundalik":
        k = datetime.now().day; gs = 10; jg = max(1, len(S)//gs); gi = k % jg
        sz = S[gi*gs:(gi+1)*gs]
        txt = f"Kundalik - {datetime.now().strftime('%d.%m.%Y')}\n\n"
        for i, s in enumerate(sz, 1): txt += f"{i}. {s['ru']} - {s['uz']}\n\n"
        bot.send_message(c, txt)
    elif t == "📚 Flashcard":
        st[c] = {"i":0,"s":0,"t":0,"a":True}; flash(c)
    elif t == "🎯 Testlar":
        st[c] = {"ti":0,"ts":0,"tt":0,"ta":True,"ca":None}; test(c)
    elif t == "📖 Barcha":
        barcha(c, 0)
    elif t == "📊 Statistika":
        bot.send_message(c, f"Jami: {len(S)}\nKorilgan: {x.get('i',0)}\nTogri: {x.get('s',0)}")
    elif t == "ℹ️ Yordam":
        bot.send_message(c, "Yordam")
    elif t == "👁 Ko'rsatish":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]
            bot.send_message(c, f"Tarjima:\n\n{s['ru']} -> {s['uz']}", reply_markup=flash_btn())
    elif t == "✅ Bilaman":
        x["s"] = x.get("s",0)+1; x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "❌ Bilmayman":
        x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
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
        x["ta"] = False; st[c] = x
        bot.send_message(c, "Menyu:", reply_markup=menu())
    else:
        bot.send_message(c, "Tugmalardan birini tanlang", reply_markup=menu())

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
    if len(bs) < 3: bot.send_message(c, "So'zlar kam."); return
    nt = random.sample(bs, 3)
    vr = [tg] + nt
    random.shuffle(vr)
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
    try: bot.polling(none_stop=True, timeout=60)
    except Exception as e: print("Xato:", e); time.sleep(5)