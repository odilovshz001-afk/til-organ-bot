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
R = {}
D = {}  # Kunlik ma'lumotlar: {user_id: {"oxirgi_kun": "07.10.2026", "streak": 3}}
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

if os.path.exists("reyting.json"):
    try: R = json.load(open("reyting.json", encoding="utf-8"))
    except: pass

if os.path.exists("kunlik.json"):
    try: D = json.load(open("kunlik.json", encoding="utf-8"))
    except: pass

print(f"JAMI: {len(S)} ta so'z")

st = {}

def saqlash():
    json.dump(U, open("users.json","w",encoding="utf-8"), ensure_ascii=False)

def reyting_saqlash():
    json.dump(R, open("reyting.json","w",encoding="utf-8"), ensure_ascii=False)

def kunlik_saqlash():
    json.dump(D, open("kunlik.json","w",encoding="utf-8"), ensure_ascii=False)

def ball_qosh(user_id, ball):
    uid = str(user_id)
    R[uid] = R.get(uid, 0) + ball
    reyting_saqlash()

def kunlik_tekshir(user_id):
    uid = str(user_id)
    bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D:
        D[uid] = {"oxirgi_kun": bugun, "streak": 1, "challenge": False}
        kunlik_saqlash()
        return 1
    if D[uid]["oxirgi_kun"] == bugun:
        return D[uid]["streak"]
    kecha = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    if D[uid]["oxirgi_kun"] == kecha:
        D[uid]["streak"] += 1
    else:
        D[uid]["streak"] = 1
    D[uid]["oxirgi_kun"] = bugun
    D[uid]["challenge"] = False
    kunlik_saqlash()
    return D[uid]["streak"]

def daraja(ball):
    if ball >= 5000: return "👑 C2 — Legenda"
    if ball >= 3000: return "🥇 C1 — Ustoz"
    if ball >= 1500: return "🥈 B2 — Ilg'or"
    if ball >= 500: return "🥉 B1 — O'rta"
    if ball >= 100: return "📗 A2 — Boshlovchi+"
    return "📘 A1 — Boshlovchi"

def yutuqlar(ball):
    yut = []
    if ball >= 100: yut.append("🥉 Boshlovchi (100)")
    if ball >= 500: yut.append("🥈 Faol (500)")
    if ball >= 1000: yut.append("🥇 Ustoz (1000)")
    if ball >= 5000: yut.append("👑 Legenda (5000)")
    return yut

def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📅 Kundalik","📚 Flashcard","🎯 Testlar","🎮 O'yin")
    m.add("🏆 Reyting","🎁 Challenge","📊 Statistika","🔄 Tarjima")
    m.add("ℹ️ Yordam")
    return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish","✅ Bilaman","❌ Bilmayman","⏹ To'xtatish")
    return m

def tarjima_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇷🇺 Ruscha → 🇺🇿 O'zbekcha","🇺🇿 O'zbekcha → 🇷🇺 Ruscha","⬅️ Orqaga")
    return m

def reyting_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🥇 TOP-10","📊 Mening reytingim","🏅 Yutuqlarim","⬅️ Orqaga")
    return m

@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "Admin"); return
    if c in U and U[c].get("ism"):
        streak = kunlik_tekshir(m.chat.id)
        ball_qosh(m.chat.id, 1)
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, f"Salom, {U[c]['ism']}! 👋\n\n📚 {len(S)} ta so'z mavjud.\n🔥 Streak: {streak} kun\n🏆 Ball: {R.get(c,0)}\n\n🎁 +1 ball!{REKLAMA}", reply_markup=menu())
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
        ball_qosh(m.chat.id, 5)
        kunlik_tekshir(m.chat.id)
        bot.send_message(c, f"Rahmat, {u['ism']}! 🎉\n\n📚 {len(S)} ta so'z mavjud.\n🎁 +5 ball!{REKLAMA}")
        try: bot.send_message(A, f"YANGI:\n{u['ism']} {u['familiya']}\n{u['tel']}")
        except: pass
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
        bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
        bot.send_message(c, "Bizni kuzatib boring 👇", reply_markup=insta_btn())

@bot.message_handler(func=lambda m: True)
def hand(m):
    c = str(m.chat.id); t = m.text
    if m.chat.id == A: return
    if c not in U or not U[c].get("ism") or U[c].get("h"): return
    if c not in st: st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False}
    x = st[c]

    # ===== O'YIN =====
    if x.get("oyin"):
        if t == "⏹ To'xtatish":
            x["oyin"] = False; st[c] = x
            bot.send_message(c, f"O'yin to'xtatildi.{REKLAMA}", reply_markup=menu())
            return
        if x.get("oyin_javob"):
            togri = x["oyin_javob"]
            if t.lower().strip() == togri.lower().strip():
                ball_qosh(m.chat.id, 10)
                x["oyin_javob"] = None
                st[c] = x
                bot.send_message(c, f"✅ To'g'ri! +10 ball\n🏆 Jami: {R.get(c,0)} ball{REKLAMA}")
                oyin_navbat(c)
            else:
                x["oyin_javob"] = None
                st[c] = x
                bot.send_message(c, f"❌ Noto'g'ri. To'g'ri javob: {togri}{REKLAMA}")
                oyin_navbat(c)
            return

    # ===== TARJIMA =====
    if x.get("tarj"):
        if t == "⬅️ Orqaga":
            x["tarj"] = False; st[c] = x
            bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
            return
        if t == "🇷🇺 Ruscha → 🇺🇿 O'zbekcha":
            x["tarj_til"] = "ru-uz"; st[c] = x
            bot.send_message(c, f"✅ Ruscha → O'zbekcha.{REKLAMA}")
            return
        if t == "🇺🇿 O'zbekcha → 🇷🇺 Ruscha":
            x["tarj_til"] = "uz-ru"; st[c] = x
            bot.send_message(c, f"✅ O'zbekcha → Ruscha.{REKLAMA}")
            return
        if TARJIMA_BOR:
            try:
                if x["tarj_til"] == "ru-uz":
                    natija = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"🇷🇺 {t}\n\n🇺🇿 {natija}{REKLAMA}")
                else:
                    natija = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"🇺🇿 {t}\n\n🇷🇺 {natija}{REKLAMA}")
            except:
                bot.send_message(c, f"❌ Tarjima xatosi.{REKLAMA}")
        return

    # ===== TEST =====
    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; ball_qosh(m.chat.id, 5)
            bot.send_message(c, f"✅ Togri! +5 ball{REKLAMA}"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"❌ Notogri. Togri: {x['ca']}{REKLAMA}"); test(c); return

    # ===== MENYU =====
    if t == "📅 Kundalik":
        ball_qosh(m.chat.id, 1)
        k = datetime.now().day; gs = 10; jg = max(1, len(S)//gs); gi = k % jg
        sz = S[gi*gs:(gi+1)*gs]
        txt = f"📅 Kundalik - {datetime.now().strftime('%d.%m.%Y')}\n\n"
        for i, s in enumerate(sz, 1): txt += f"{i}. {s['ru']} - {s['uz']}\n\n"
        txt += f"🎁 +1 ball\n🏆 Jami: {R.get(c,0)}{REKLAMA}"
        bot.send_message(c, txt)
    elif t == "📚 Flashcard":
        st[c] = {"i":0,"s":0,"t":0,"a":True,"tarj":False,"tarj_til":"ru-uz","oyin":False}; flash(c)
    elif t == "🎯 Testlar":
        st[c] = {"ti":0,"ts":0,"tt":0,"ta":True,"ca":None,"tarj":False,"oyin":False}; test(c)
    elif t == "🎮 O'yin":
        st[c] = {"oyin":True,"oyin_javob":None,"tarj":False,"a":False}; oyin_navbat(c)
    elif t == "🎁 Challenge":
        challenge(c)
    elif t == "🏆 Reyting":
        bot.send_message(c, f"🏆 Reyting menyusi:{REKLAMA}", reply_markup=reyting_menu())
    elif t == "🥇 TOP-10":
        top10(c)
    elif t == "📊 Mening reytingim":
        mening_reyting(c)
    elif t == "🏅 Yutuqlarim":
        ball = R.get(c, 0)
        yut = yutuqlar(ball)
        txt = f"🏅 *Yutuqlaringiz*\n\n🏆 Ball: {ball}\n📊 Daraja: {daraja(ball)}\n\n"
        if yut:
            txt += "✅ Yutuqlar:\n" + "\n".join(yut)
        else:
            txt += "Hozircha yutuq yo'q. O'ynang va yutuqlarga erishing!"
        txt += REKLAMA
        bot.send_message(c, txt, parse_mode='Markdown')
    elif t == "📊 Statistika":
        ball = R.get(c, 0)
        streak = D.get(c, {}).get("streak", 0)
        bot.send_message(c, f"📊 *Statistika*\n\n📚 Jami so'zlar: {len(S)}\n📖 Ko'rilgan: {x.get('i',0)}\n✅ To'g'ri: {x.get('s',0)}\n\n🏆 Ball: {ball}\n📊 Daraja: {daraja(ball)}\n🔥 Streak: {streak} kun{REKLAMA}", parse_mode='Markdown')
    elif t == "ℹ️ Yordam":
        bot.send_message(c, f"📖 *Yordam*\n\n📅 Kundalik — kunlik so'zlar (+1)\n📚 Flashcard — so'z yodlash (+2)\n🎯 Testlar — bilim sinash (+5)\n🎮 O'yin — so'z topish (+10)\n🎁 Challenge — kunlik topshiriq (+20)\n🏆 Reyting — TOP-10 va yutuqlar\n🔄 Tarjima — matn tarjimasi{REKLAMA}", parse_mode='Markdown')
    elif t == "👁 Ko'rsatish":
        idx = x.get("i",0)
        if idx < len(S):
            s = S[idx]
            bot.send_message(c, f"Tarjima:\n\n{s['ru']} -> {s['uz']}{REKLAMA}", reply_markup=flash_btn())
    elif t == "✅ Bilaman":
        ball_qosh(m.chat.id, 2)
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
        x["ta"] = False; x["tarj"] = False; x["oyin"] = False; st[c] = x
        bot.send_message(c, f"Menyu:{REKLAMA}", reply_markup=menu())
    else:
        if TARJIMA_BOR and len(t) > 2:
            try:
                natija = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"📝 Tarjima:\n\n🇷🇺 {t}\n\n🇺🇿 {natija}{REKLAMA}")
                return
            except: pass
        bot.send_message(c, f"Tugmalardan birini tanlang{REKLAMA}", reply_markup=menu())

def challenge(c):
    uid = str(c)
    bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D:
        D[uid] = {"oxirgi_kun": bugun, "streak": 1, "challenge": False}
    if D[uid].get("challenge"):
        bot.send_message(c, f"✅ Bugungi challenge bajarilgan!\n\nErtaga yangi topshiriq.{REKLAMA}", reply_markup=menu())
        return
    if len(S) < 4:
        bot.send_message(c, f"So'zlar kam.{REKLAMA}")
        return
    s = random.choice(S)
    st[c] = {"challenge": True, "javob": s["uz"], "tarj": False, "oyin": False, "a": False}
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⏹ To'xtatish")
    bot.send_message(c, f"🎁 *Kunlik Challenge*\n\nRuscha: *{s['ru']}*\n\nO'zbekcha tarjimasini yozing:\n🎁 +20 ball{REKLAMA}", parse_mode='Markdown', reply_markup=mk)

def oyin_navbat(c):
    x = st.get(c, {})
    if len(S) < 4:
        bot.send_message(c, f"So'zlar kam.{REKLAMA}", reply_markup=menu()); return
    s = random.choice(S)
    x["oyin_javob"] = s["uz"]
    x["oyin"] = True
    st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⏹ To'xtatish")
    bot.send_message(c, f"🎮 O'yin\n\nRuscha: *{s['ru']}*\n\nO'zbekcha tarjimasini yozing:\n🎁 +10 ball{REKLAMA}", parse_mode='Markdown', reply_markup=mk)

def top10(c):
    if not R:
        bot.send_message(c, f"🏆 Hozircha reyting bo'sh.{REKLAMA}"); return
    saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "🏆 *TOP-10*\n\n"
    medallar = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, ball) in enumerate(saralangan):
        ism = U.get(uid, {}).get("ism", "Noma'lum")
        txt += f"{medallar[i]} {ism} — {ball} ball\n"
    txt += REKLAMA
    bot.send_message(c, txt, parse_mode='Markdown')

def mening_reyting(c):
    ball = R.get(str(c), 0)
    if not R:
        orin = 1
    else:
        saralangan = sorted(R.items(), key=lambda x: x[1], reverse=True)
        orin = 1
        for i, (uid, b) in enumerate(saralangan, 1):
            if uid == str(c):
                orin = i
                break
    streak = D.get(c, {}).get("streak", 0)
    bot.send_message(c, f"📊 *Sizning reytingingiz*\n\n🏆 Ball: *{ball}*\n📍 O'rin: *{orin}* / {len(R)}\n📊 Daraja: {daraja(ball)}\n🔥 Streak: {streak} kun{REKLAMA}", parse_mode='Markdown')

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