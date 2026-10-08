# -*- coding: utf-8 -*-
import os, json, time, random, re, logging, sqlite3
from threading import Thread, Lock
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import telebot
from telebot import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

T = os.environ.get("BOT_TOKEN", "")
A = int(os.environ.get("ADMIN_ID", "8178917212"))
ADMIN_PASS = os.environ.get("ADMIN_PASS", "Alijonodilov77$$")

if not T:
    log.error("BOT_TOKEN yo'q!"); exit(1)
try:
    from deep_translator import GoogleTranslator
    TARJIMA_BOR = True
except ImportError:
    TARJIMA_BOR = False

log.info(f"✅ Bot ishga tushmoqda... Asosiy admin: {A}")

class HH(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), HH).serve_forever(), daemon=True).start()
bot = telebot.TeleBot(T, num_threads=8)

DB = "bot_data.db"
dblock = Lock()
ADMINS = set()

def db(sql, p=(), f=False):
    with dblock:
        conn = sqlite3.connect(DB, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        c = conn.cursor(); c.execute(sql, p)
        r = [dict(x) for x in c.fetchall()] if f else None
        conn.commit(); conn.close(); return r

def db_init():
    with dblock:
        conn = sqlite3.connect(DB, check_same_thread=False)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, ism TEXT, familiya TEXT,
            sana_tugilgan TEXT, tel TEXT, h TEXT DEFAULT '',
            ball INTEGER DEFAULT 0, streak INTEGER DEFAULT 0,
            oxirgi_kun TEXT DEFAULT '', sovga_kun TEXT DEFAULT '',
            sana TEXT DEFAULT '', aktiv INTEGER DEFAULT 1,
            oxirgi_soz TEXT DEFAULT '', oxirgi_test TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sevimlilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            soz_ru TEXT, UNIQUE(user_id, soz_ru))""")
        c.execute("""CREATE TABLE IF NOT EXISTS dostlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            dost_id INTEGER, UNIQUE(user_id, dost_id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS talablar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            matn TEXT, sana TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY, ism TEXT, sana TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS admin_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, ism TEXT, amal TEXT, sana TEXT)""")
        defaults = {
            "reklama": "📢 *Bizni kuzatib boring!*\n\n📸 Instagram: @odilov03_\n💬 Telegram: @odilov0_3",
            "reklama_instagram": "https://instagram.com/odilov03_",
            "reklama_telegram": "https://t.me/odilov0_3",
            "reklama_auto": "1",
            "reklama_vaqt": "09:00",
            "soz_auto": "1",
            "soz_interval": "300",
            "test_auto": "1",
            "test_interval": "600",
            "sovga_min": "10",
            "sovga_max": "100"
        }
        for k, v in defaults.items():
            c.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (k, v))
        conn.commit(); conn.close()
    log.info("✅ SQLite tayyor")

db_init()

def admins_init():
    global ADMINS
    ADMINS = {A}
    r = db("SELECT user_id FROM admins", (), True)
    for row in r or []:
        ADMINS.add(row["user_id"])
    log.info(f"✅ Adminlar: {len(ADMINS)}")

admins_init()

def u_get(uid):
    r = db("SELECT * FROM users WHERE user_id = ?", (uid,), True)
    return r[0] if r else None

def u_create(uid):
    db("INSERT OR IGNORE INTO users (user_id, sana) VALUES (?, ?)",
       (uid, datetime.now().strftime("%d.%m.%Y %H:%M")))

def u_upd(uid, **kw):
    if not kw: return
    k = ", ".join(f"{x} = ?" for x in kw)
    db(f"UPDATE users SET {k} WHERE user_id = ?", list(kw.values()) + [uid])

def ball_qosh(uid, b):
    db("UPDATE users SET ball = ball + ? WHERE user_id = ?", (b, uid))

def ball_get(uid):
    r = db("SELECT ball FROM users WHERE user_id = ?", (uid,), True)
    return r[0]["ball"] if r else 0

def cfg_get(k, d=""):
    r = db("SELECT value FROM config WHERE key = ?", (k,), True)
    return r[0]["value"] if r else d

def cfg_set(k, v):
    db("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (k, str(v)))

def log_admin(uid, ism, amal):
    db("INSERT INTO admin_log (user_id, ism, amal, sana) VALUES (?, ?, ?, ?)",
       (uid, ism or "?", amal, datetime.now().strftime("%d.%m.%Y %H:%M")))

S, kor, KUNDALIK_GAPLAR = [], set(), []

for f in ["sozlar.json", "sozlar_katta.json", "sozlar_qoshimcha.json", "sozlar_ish.json", "sozlar_vaqt.json"]:
    if os.path.exists(f):
        try:
            with open(f, encoding="utf-8") as fp:
                d = json.load(fp)
            for s in d.get("sozlar", []):
                if s.get("ru") and s["ru"] not in kor:
                    S.append(s); kor.add(s["ru"])
        except Exception as e:
            log.error(f"{f}: {e}")

for fname in ["kundalik_gaplar.json", "kundalik_gaplar2.json"]:
    if os.path.exists(fname):
        try:
            with open(fname, encoding="utf-8") as fp:
                KUNDALIK_GAPLAR.extend(json.load(fp).get("gaplar", []))
        except Exception as e:
            log.error(f"{fname}: {e}")

log.info(f"📚 So'zlar: {len(S)}, Gaplar: {len(KUNDALIK_GAPLAR)}")

def reklama_btn():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("📸 Instagram", url=cfg_get("reklama_instagram", "https://instagram.com/odilov03_")),
        types.InlineKeyboardButton("💬 Telegram", url=cfg_get("reklama_telegram", "https://t.me/odilov0_3"))
    )
    return m

def reklama_matn():
    return cfg_get("reklama", "📢 Bizni kuzatib boring!")

SUHBAT_GAPLAR = {
    "💼 Ishda": [
        {"ru": "Доброе утро!", "uz": "Xayrli tong!"},
        {"ru": "Как ваши дела?", "uz": "Ishlaringiz qanday?"},
        {"ru": "Что нового?", "uz": "Nima yangilik?"},
        {"ru": "Я готов к работе.", "uz": "Men ishga tayyorman."},
        {"ru": "Давайте начнём.", "uz": "Keling, boshlaymiz."},
        {"ru": "Сколько времени?", "uz": "Soat necha?"},
        {"ru": "Спасибо за помощь.", "uz": "Rahmat."},
        {"ru": "Хорошего дня!", "uz": "Yaxshi kun!"},
        {"ru": "До завтра!", "uz": "Ertagagacha!"}
    ],
    "🚶 Ko'chada": [
        {"ru": "Извините, как пройти?", "uz": "Kechirasiz, qanday boriladi?"},
        {"ru": "Где находится метро?", "uz": "Metro qayerda?"},
        {"ru": "Это далеко?", "uz": "Bu uzoqmi?"},
        {"ru": "Сколько стоит такси?", "uz": "Taksi qancha?"},
        {"ru": "Я заблудился.", "uz": "Men adashdim."},
        {"ru": "Где выход?", "uz": "Chiqish qayerda?"},
        {"ru": "Спасибо большое!", "uz": "Katta rahmat!"},
        {"ru": "До свидания!", "uz": "Xayr!"}
    ],
    "🛒 Do'konda": [
        {"ru": "Сколько это стоит?", "uz": "Bu qancha?"},
        {"ru": "Это дорого.", "uz": "Bu qimmat."},
        {"ru": "Есть дешевле?", "uz": "Arzonroq bormi?"},
        {"ru": "Дайте, пожалуйста.", "uz": "Bering."},
        {"ru": "Можно картой?", "uz": "Karta bilan?"},
        {"ru": "Спасибо за покупку!", "uz": "Rahmat!"},
        {"ru": "Хорошего дня!", "uz": "Yaxshi kun!"}
    ],
    "☕ Suhbatda": [
        {"ru": "Привет! Как дела?", "uz": "Salom! Qalaysiz?"},
        {"ru": "Меня зовут...", "uz": "Mening ismim..."},
        {"ru": "Очень приятно!", "uz": "Juda yoqimli!"},
        {"ru": "Откуда вы?", "uz": "Qayerdansiz?"},
        {"ru": "Сколько вам лет?", "uz": "Yoshingiz?"},
        {"ru": "До встречи!", "uz": "Ko'rishguncha!"}
    ]
}

KATEGORIYALAR = {
    "👋 Salomlashish": ["Привет", "Спасибо", "Пожалуйста", "Да", "Нет"],
    "🍞 Oziq-ovqat": ["Вода", "Хлеб", "Чай", "Кофе", "Молоко"],
    "👨‍👩‍👧 Oila": ["Мама", "Папа", "Брат", "Сестра", "Семья"],
    "💼 Ish": ["Работа", "Учитель", "Книга", "Стол"],
    "⏰ Vaqt": ["Время", "День", "Ночь", "Утро", "Вечер"]
}

GAPLAR = [
    {"togri": "Я люблю чай", "sozlar": ["чай", "люблю", "Я"], "tarjima": "Men choyni yaxshi ko'raman"},
    {"togri": "Как дела", "sozlar": ["дела", "Как"], "tarjima": "Qalaysan"},
    {"togri": "Спасибо большое", "sozlar": ["большое", "Спасибо"], "tarjima": "Katta rahmat"},
    {"togri": "Я хочу воду", "sozlar": ["воду", "хочу", "Я"], "tarjima": "Men suv xohlayman"}
]

GRAMMATIKA = {
    "📘 Fe'l zamonlari": "Настоящее: Я читаю\nПрошедшее: Я читал\nБудущее: Я буду читать",
    "📗 Kelishiklar": "Им: стол\nРод: стола\nДат: столу",
    "📙 Sonlar": "1 один\n2 два\n3 три\n4 четыре\n5 пять",
    "📕 Ranglar": "красный — qizil\nсиний — ko'k\nзелёный — yashil"
}

CHAT_SAVOLLAR = [
    {"savol": "Как тебя зовут?", "javob": "Меня зовут..."},
    {"savol": "Откуда ты?", "javob": "Я из..."},
    {"savol": "Сколько тебе лет?", "javob": "Мне ... лет"}
]

st = {}

def gs(c):
    if c not in st: st[c] = {}
    return st[c]

def ss(c, **kw):
    x = gs(c); x.update(kw); st[c] = x; return x

def cs(c):
    st[c] = {}

def ism_ok(s):
    if not s or len(s) < 2: return False
    if not re.match(r'^[\w\s\'-]{2,50}$', s, re.UNICODE): return False
    if s.strip().isdigit(): return False
    return True

def tel_ok(t):
    t = re.sub(r'[^\d+]', '', t)
    return bool(re.match(r'^\+?\d{10,15}$', t))

def sana_ok(s):
    try:
        d = datetime.strptime(s, "%d.%m.%Y")
        return 5 <= (datetime.now().year - d.year) <= 120
    except: return False

def kunlik(uid):
    u = u_get(uid)
    bugun = datetime.now().strftime("%d.%m.%Y")
    if not u: return 1
    if u["oxirgi_kun"] == bugun: return u["streak"]
    kecha = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    st_new = u["streak"] + 1 if u["oxirgi_kun"] == kecha else 1
    u_upd(uid, oxirgi_kun=bugun, streak=st_new, sovga_kun="")
    return st_new

def daraja(b):
    if b >= 5000: return "👑 C2"
    if b >= 3000: return "🥇 C1"
    if b >= 1500: return "🥈 B2"
    if b >= 500: return "🥉 B1"
    if b >= 100: return "📗 A2"
    return "📘 A1"

def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📅 Kundalik", "📚 Flashcard", "🎯 Testlar", "🎮 O'yin")
    m.add("💬 Suhbat", "📝 Gap tuzish", "📚 Kategoriya", "🎵 Talaffuz")
    m.add("🎁 Sovga", "👥 Do'stlar", "⭐ Sevimlilar", "🏆 Reyting")
    m.add("📖 Grammatika", "💬 Chat", "📊 Statistika", "🔄 Tarjima")
    m.add("📢 Talab va taklif", "ℹ️ Yordam")
    return m

def admin_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📊 Statistika", "👥 Foydalanuvchilar")
    m.add("📢 Reklama sozlash", "📚 So'z sozlash")
    m.add("🎯 Test sozlash", "✉️ Xabar yuborish")
    m.add("📋 Talablar", "🎁 Sovga sozlash")
    m.add("🗑 Ban qilish", "🔐 Xavfsizlik")
    m.add("⬅️ Chiqish")
    return m

def xavfsizlik_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👥 Adminlar", "➕ Admin qo'shish")
    m.add("➖ Admin o'chirish", "🔑 Parol ko'rish")
    m.add("📜 Admin loglar", "⬅️ Orqaga")
    return m

def rek_admin_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("✏️ Matn", "📸 Instagram", "💬 Telegram")
    m.add("🔄 Avto reklama", "⏰ Reklama vaqti", "👁 Ko'rish")
    m.add("⬅️ Orqaga")
    return m

def soz_admin_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🔄 Avto so'z", "⏱ Interval", "👁 Hozir yuborish")
    m.add("⬅️ Orqaga")
    return m

def test_admin_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🔄 Avto test", "⏱ Test interval", "👁 Hozir yuborish")
    m.add("⬅️ Orqaga")
    return m

def kun_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🔊 Eshitish", "🔄 Yangilash", "⬅️ Orqaga")
    return m

def suh_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in SUHBAT_GAPLAR.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish", "✅ Bilaman", "❌ Bilmayman", "⭐ Saqlash")
    m.add("🔊 Eshitish", "⏹ To'xtatish")
    return m

def rey_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🥇 TOP-10", "📊 Mening reytingim", "🏅 Yutuqlarim", "⬅️ Orqaga")
    return m

def kat_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in KATEGORIYALAR.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def dost_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("🔗 Havola", "👥 Do'stlarim", "⬅️ Orqaga")
    return m

def gram_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in GRAMMATIKA.keys(): m.add(k)
    m.add("⬅️ Orqaga")
    return m

def tal_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("📢 Talab yozish", "📋 Mening talablarim", "⬅️ Orqaga")
    return m

def gap_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("⏹ To'xtatish")
    return m

def tarj_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇷🇺 → 🇺🇿", "🇺🇿 → 🇷🇺", "⬅️ Orqaga")
    return m

def soz_bilaman_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("✅ Bilaman", "❌ Bilmadim")
    return m

def kundalik_gaplar(c):
    if not KUNDALIK_GAPLAR:
        bot.send_message(c, "Gaplar yo'q."); return
    gaplar = random.sample(KUNDALIK_GAPLAR, min(10, len(KUNDALIK_GAPLAR)))
    txt = f"💬 *Kundalik gaplar*\n📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    for i, g in enumerate(gaplar, 1):
        txt += f"*{i}.* 🇷🇺 {g['ru']}\n     🇺🇿 _{g['uz']}_\n\n"
    txt += f"🏆 Jami: {ball_get(c)}\n📚 Jami: {len(KUNDALIK_GAPLAR)} ta"
    ss(c, kundalik_gaplar=gaplar)
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=kun_menu())

def suhbat_korsat(c):
    x = gs(c)
    kat = x.get("suhbat_kat")
    i = x.get("suhbat_i", 0)
    if not kat: return
    gaplar = SUHBAT_GAPLAR[kat]
    if i >= len(gaplar):
        ss(c, suhbat_kat=None)
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    gap = gaplar[i]
    txt = f"💬 *{kat}* ({i+1}/{len(gaplar)})\n\n🇷🇺 *{gap['ru']}*\n\n🇺🇿 {gap['uz']}"
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    mk.add("🔊 Eshitish", "⬅️ Oldingi", "➡️ Keyingi")
    mk.add("⬅️ Orqaga")
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=mk)

def next_savol(c):
    savol = random.choice(CHAT_SAVOLLAR)
    ss(c, chat=True, chat_savol=savol)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⬅️ Orqaga")
    bot.send_message(c, f"💬 *Chat*\n\n{savol['savol']}\n\n_Ruscha javob yozing_",
                     parse_mode='Markdown', reply_markup=mk)

def gap_tuzish(c):
    g = random.choice(GAPLAR)
    sozlar = g["sozlar"].copy(); random.shuffle(sozlar)
    st[c] = {"gap": True, "gap_togri": g["togri"]}
    txt = "📝 *Gap tuzish*\n\nSo'zlardan gap tuzing:\n\n"
    for s in sozlar: txt += f"• {s}\n"
    txt += f"\n💡 _{g['tarjima']}_\n🎁 +15 ball"
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=gap_menu())

def sovga(c):
    u = u_get(c)
    bugun = datetime.now().strftime("%d.%m.%Y")
    if not u: return
    if u.get("sovga_kun") == bugun:
        bot.send_message(c, "Bugungi sovgani oldingiz!", reply_markup=menu()); return
    ball = random.randint(int(cfg_get("sovga_min", "10")), int(cfg_get("sovga_max", "100")))
    ball_qosh(c, ball); u_upd(c, sovga_kun=bugun)
    bot.send_message(c, f"🎁 *Sovga!*\n\n+{ball} ball!\n🏆 Jami: {ball_get(c)}",
                     parse_mode='Markdown', reply_markup=menu())

def talaffuz(c):
    if not S: return
    s = random.choice(S)
    st[c] = {"talaffuz": s}
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("🔊 Eshitish", "👁 Tarjima", "➡️ Keyingi so'z", "⏹ To'xtatish")
    bot.send_message(c, f"🎵 *Talaffuz*\n\nRuscha: *{s['ru']}*",
                     parse_mode='Markdown', reply_markup=mk)

def yutuqlarim(c):
    ball = ball_get(c)
    u = u_get(c) or {}
    streak = u.get("streak", 0)
    d = db("SELECT COUNT(*) as n FROM dostlar WHERE user_id = ?", (c,), True)
    dostlar = d[0]["n"] if d else 0
    txt = "🏅 *Yutuqlaringiz*\n\n"
    if ball >= 1000: txt += "✅ 👑 Legenda (1000)\n"
    elif ball >= 500: txt += "✅ 🥇 Ustoz (500)\n"
    elif ball >= 100: txt += "✅ 🥈 Faol (100)\n"
    elif ball >= 10: txt += "✅ 🥉 Birinchi (10)\n"
    else: txt += "⏳ 🥉 Birinchi (10)\n"
    txt += f"{'✅' if streak >= 7 else '⏳'} 🔥 7 kun ({streak}/7)\n"
    txt += f"{'✅' if dostlar >= 1 else '⏳'} 👥 Do'st ({dostlar}/1)"
    bot.send_message(c, txt, parse_mode='Markdown')

def grafik(c):
    ball = ball_get(c)
    txt = "📊 *Grafik*\n\n"
    for d in [0, 100, 500, 1500, 3000, 5000]:
        txt += f"{'✅' if ball >= d else '⬜'} {d} ball\n"
    txt += f"\n🏆 Siz: {ball}\n📊 {daraja(ball)}"
    bot.send_message(c, txt, parse_mode='Markdown')

def sevimlilar(c):
    r = db("SELECT soz_ru FROM sevimlilar WHERE user_id = ?", (c,), True)
    if not r:
        bot.send_message(c, "⭐ Bo'sh."); return
    txt = "⭐ *Sevimlilar:*\n\n"
    for i, row in enumerate(r, 1):
        for s in S:
            if s["ru"] == row["soz_ru"]:
                txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
    bot.send_message(c, txt, parse_mode='Markdown')

def top10(c):
    r = db("SELECT user_id, ball FROM users ORDER BY ball DESC LIMIT 10", (), True)
    if not r:
        bot.send_message(c, "🏆 Bo'sh."); return
    txt = "🏆 *TOP-10*\n\n"
    med = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, row in enumerate(r):
        u = u_get(row["user_id"])
        ism = u.get("ism", "?") if u else "?"
        txt += f"{med[i]} {ism} — {row['ball']}\n"
    bot.send_message(c, txt, parse_mode='Markdown')

def mening_reyting(c):
    ball = ball_get(c)
    r = db("SELECT COUNT(*) as n FROM users WHERE ball > ?", (ball,), True)
    orin = (r[0]["n"] + 1) if r else 1
    total = db("SELECT COUNT(*) as n FROM users", (), True)
    total = total[0]["n"] if total else 0
    u = u_get(c) or {}; streak = u.get("streak", 0)
    bot.send_message(c, f"📊 *Reytingingiz*\n\n🏆 Ball: *{ball}*\n📍 O'rin: *{orin}* / {total}\n📊 {daraja(ball)}\n🔥 Streak: {streak} kun",
                     parse_mode='Markdown')

def flash(c):
    x = gs(c); idx = x.get("i", 0)
    if not S or idx >= len(S):
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    s = S[idx]
    bot.send_message(c, f"Flashcard ({idx+1}/{len(S)})\n\nRuscha: {s['ru']}",
                     reply_markup=flash_btn())

def test(c):
    x = gs(c); idx = x.get("ti", 0)
    if not S or idx >= len(S):
        sc = x.get("ts", 0); tt = x.get("tt", 0)
        ss(c, ta=False)
        bot.send_message(c, f"Tugadi!\n\nJami: {tt}\nTo'g'ri: {sc}", reply_markup=menu()); return
    tg = S[idx]
    bs = [s for s in S if s["uz"] != tg["uz"]]
    if len(bs) < 3:
        bot.send_message(c, "So'zlar kam."); return
    nt = random.sample(bs, 3); vr = [tg] + nt; random.shuffle(vr)
    ss(c, ca=tg["uz"])
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for v in vr: mk.add(v["uz"])
    mk.add("⏹ Testdan chiqish")
    bot.send_message(c, f"Test ({idx+1}/{len(S)})\n\n{tg['ru']} - ?", reply_markup=mk)

def oyin_navbat(c):
    if len(S) < 4:
        bot.send_message(c, "So'zlar kam.", reply_markup=menu()); return
    s = random.choice(S)
    ss(c, oyin_javob=s["uz"], oyin=True)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⏹ To'xtatish")
    bot.send_message(c, f"🎮 *O'yin*\n\nRuscha: *{s['ru']}*\n\nTarjima yozing\n🎁 +10 ball",
                     parse_mode='Markdown', reply_markup=mk)

def admin_statistika():
    bugun = datetime.now().strftime("%d.%m.%Y")
    t_u = db("SELECT COUNT(*) as n FROM users", (), True); t_u = t_u[0]["n"] if t_u else 0
    b_u = db("SELECT COUNT(*) as n FROM users WHERE sana LIKE ?", (bugun + "%",), True); b_u = b_u[0]["n"] if b_u else 0
    a_u = db("SELECT COUNT(*) as n FROM users WHERE oxirgi_kun = ?", (bugun,), True); a_u = a_u[0]["n"] if a_u else 0
    t_t = db("SELECT COUNT(*) as n FROM talablar", (), True); t_t = t_t[0]["n"] if t_t else 0
    t_s = db("SELECT COUNT(*) as n FROM sevimlilar", (), True); t_s = t_s[0]["n"] if t_s else 0
    t_d = db("SELECT COUNT(*) as n FROM dostlar", (), True); t_d = t_d[0]["n"] if t_d else 0
    return (
        "📊 *BOT STATISTIKASI*\n\n"
        f"👥 Jami: *{t_u}*\n"
        f"📅 Bugun: *{b_u}*\n"
        f"🔥 Aktiv: *{a_u}*\n"
        f"📚 So'zlar: *{len(S)}*\n"
        f"💬 Gaplar: *{len(KUNDALIK_GAPLAR)}*\n"
        f"⭐ Sevimlilar: *{t_s}*\n"
        f"👫 Do'stlik: *{t_d}*\n"
        f"📢 Talablar: *{t_t}*\n"
        f"👑 Adminlar: *{len(ADMINS)}*\n\n"
        f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

def reklama_loop():
    oxirgi = ""
    while True:
        try:
            if cfg_get("reklama_auto", "1") != "1":
                time.sleep(60); continue
            vaqt = cfg_get("reklama_vaqt", "09:00")
            hozir = datetime.now().strftime("%H:%M")
            bugun = datetime.now().strftime("%d.%m.%Y")
            if hozir == vaqt and oxirgi != bugun:
                matn = reklama_matn()
                r = db("SELECT user_id FROM users WHERE aktiv = 1", (), True)
                for row in r or []:
                    try:
                        bot.send_message(row["user_id"], matn, parse_mode='Markdown', reply_markup=reklama_btn())
                        time.sleep(0.05)
                    except: pass
                oxirgi = bugun
                log.info(f"✅ Reklama: {bugun}")
            time.sleep(30)
        except Exception as e:
            log.error(f"Reklama: {e}"); time.sleep(60)

def soz_loop():
    while True:
        try:
            if cfg_get("soz_auto", "1") != "1":
                time.sleep(60); continue
            interval = int(cfg_get("soz_interval", "300"))
            time.sleep(interval)
            if not S: continue
            bugun = datetime.now().strftime("%d.%m.%Y")
            r = db("SELECT user_id FROM users WHERE oxirgi_kun = ?", (bugun,), True)
            for row in r or []:
                try:
                    uid = row["user_id"]
                    u = u_get(uid)
                    oxirgi = u.get("oxirgi_soz", "") if u else ""
                    yangi = None
                    for _ in range(5):
                        s = random.choice(S)
                        if s["ru"] != oxirgi:
                            yangi = s; break
                    if not yangi: yangi = random.choice(S)
                    u_upd(uid, oxirgi_soz=yangi["ru"])
                    ss(str(uid), soz_yangi=yangi)
                    bot.send_message(
                        uid,
                        f"📚 *Yangi so'z!*\n\n🇷🇺 *{yangi['ru']}*\n🇺🇿 _{yangi['uz']}_\n\nEslab qoldingizmi?",
                        parse_mode='Markdown',
                        reply_markup=soz_bilaman_menu()
                    )
                    time.sleep(0.1)
                except: pass
        except Exception as e:
            log.error(f"So'z loop: {e}"); time.sleep(60)

def test_loop():
    while True:
        try:
            if cfg_get("test_auto", "1") != "1":
                time.sleep(60); continue
            interval = int(cfg_get("test_interval", "600"))
            time.sleep(interval)
            if not S: continue
            bugun = datetime.now().strftime("%d.%m.%Y")
            r = db("SELECT user_id FROM users WHERE oxirgi_kun = ?", (bugun,), True)
            for row in r or []:
                try:
                    uid = row["user_id"]
                    u = u_get(uid)
                    oxirgi = u.get("oxirgi_test", "") if u else ""
                    tg = None
                    for _ in range(5):
                        s = random.choice(S)
                        if s["ru"] != oxirgi:
                            tg = s; break
                    if not tg: tg = random.choice(S)
                    bs = [s for s in S if s["uz"] != tg["uz"]]
                    if len(bs) < 3: continue
                    nt = random.sample(bs, 3)
                    vr = [tg] + nt; random.shuffle(vr)
                    u_upd(uid, oxirgi_test=tg["ru"])
                    ss(str(uid), auto_test_javob=tg["uz"])
                    mk = types.InlineKeyboardMarkup(row_width=2)
                    btns = []
                    for v in vr:
                        btns.append(types.InlineKeyboardButton(v["uz"], callback_data=f"autotest_{uid}_{v['uz']}"))
                    mk.add(*btns)
                    bot.send_message(
                        uid,
                        f"🎯 *TEST!*\n\n🇷🇺 *{tg['ru']}*\n\nTo'g'ri javobni tanlang:\n🎁 +5 ball",
                        parse_mode='Markdown',
                        reply_markup=mk
                    )
                    time.sleep(0.1)
                except: pass
        except Exception as e:
            log.error(f"Test loop: {e}"); time.sleep(60)

Thread(target=reklama_loop, daemon=True).start()
Thread(target=soz_loop, daemon=True).start()
Thread(target=test_loop, daemon=True).start()
@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "👑 *ADMIN PANEL*", parse_mode='Markdown', reply_markup=admin_menu())
        return
    if len(m.text.split()) > 1:
        try:
            taklif = m.text.split()[1]
            if taklif.isdigit() and int(taklif) != m.chat.id:
                db("INSERT OR IGNORE INTO dostlar (user_id, dost_id) VALUES (?, ?)", (int(taklif), m.chat.id))
                db("INSERT OR IGNORE INTO dostlar (user_id, dost_id) VALUES (?, ?)", (m.chat.id, int(taklif)))
                ball_qosh(m.chat.id, 50)
                ball_qosh(int(taklif), 50)
        except: pass
    u = u_get(m.chat.id)
    if u and u.get("ism"):
        streak = kunlik(m.chat.id)
        ball_qosh(m.chat.id, 1)
        cs(c)
        bot.send_message(
            c,
            f"Salom, {u['ism']}! 👋\n\n"
            f"📚 {len(S)} so'z\n"
            f"💬 {len(KUNDALIK_GAPLAR)} gap\n"
            f"🔥 Streak: {streak}\n"
            f"🏆 Ball: {ball_get(m.chat.id)}\n"
            f"🎁 +1 ball!",
            reply_markup=menu()
        )
        try:
            bot.send_message(c, reklama_matn(), parse_mode='Markdown', reply_markup=reklama_btn())
        except: pass
        return
    u_create(m.chat.id)
    u_upd(m.chat.id, h="ism")
    bot.send_message(c, "🌍 Assalomu alaykum!\n\n📝 Ismingizni kiriting:",
                     reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    c = str(m.chat.id)
    if m.chat.id in ADMINS:
        bot.send_message(c, "👑 *ADMIN PANEL*", parse_mode='Markdown', reply_markup=admin_menu())
        return
    ss(c, admin_parol=True)
    bot.send_message(c, "🔐 *Admin parolini kiriting:*", parse_mode='Markdown',
                     reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: str(m.chat.id) != str(A) and u_get(m.chat.id) and u_get(m.chat.id).get("h"))
def reg(m):
    if not m.text: return
    c = str(m.chat.id)
    u = u_get(m.chat.id)
    t = m.text.strip()
    h = u.get("h")
    if h == "ism":
        if not ism_ok(t):
            bot.send_message(c, "❌ Ism noto'g'ri!\nQaytadan:"); return
        u_upd(m.chat.id, ism=t, h="fam")
        bot.send_message(c, "✅ Familiyangizni kiriting:")
    elif h == "fam":
        if not ism_ok(t):
            bot.send_message(c, "❌ Familiya noto'g'ri!\nQaytadan:"); return
        u_upd(m.chat.id, familiya=t, h="sana")
        bot.send_message(c, "✅ Tug'ilgan sana:\n\nFormat: DD.MM.YYYY")
    elif h == "sana":
        if not sana_ok(t):
            bot.send_message(c, "❌ Sana noto'g'ri!\nFormat: DD.MM.YYYY"); return
        u_upd(m.chat.id, sana_tugilgan=t, h="tel")
        bot.send_message(c, "✅ Telefon:\n\nFormat: +998901234567")
    elif h == "tel":
        if not tel_ok(t):
            bot.send_message(c, "❌ Telefon noto'g'ri!\nFormat: +998901234567"); return
        u_upd(m.chat.id, tel=t, h="")
        ball_qosh(m.chat.id, 5)
        kunlik(m.chat.id)
        bot.send_message(c, f"🎉 Rahmat, {u['ism']}!\n\n🎁 +5 ball!")
        try:
            bot.send_message(c, reklama_matn(), parse_mode='Markdown', reply_markup=reklama_btn())
        except: pass
        try:
            bot.send_message(A, f"👤 YANGI:\n{u['ism']} {u.get('familiya','')}\n{u.get('sana_tugilgan','')}\n{u['tel']}")
        except: pass
        cs(c)
        bot.send_message(c, "Menyu:", reply_markup=menu())

@bot.message_handler(func=lambda m: m.chat.id == A, content_types=['text'])
def admin_handler(m):
    c = str(m.chat.id)
    t = m.text
    x = gs(c)
    if x.get("admin_parol"):
        if t == ADMIN_PASS:
            ADMINS.add(m.chat.id)
            db("INSERT OR IGNORE INTO admins (user_id, ism, sana) VALUES (?, ?, ?)",
               (m.chat.id, m.from_user.first_name or "?", datetime.now().strftime("%d.%m.%Y %H:%M")))
            log_admin(m.chat.id, m.from_user.first_name, "Admin bo'ldi")
            ss(c, admin_parol=False)
            bot.send_message(c, "✅ *Tasdiqlandi!*\n\n👑 Admin panel:", parse_mode='Markdown', reply_markup=admin_menu())
            log.info(f"✅ Yangi admin: {m.chat.id}")
        else:
            ss(c, admin_parol=False)
            bot.send_message(c, "❌ Noto'g'ri parol!")
        return

    if x.get("admin_holat"):
        h = x["admin_holat"]
        if h == "reklama_matn": cfg_set("reklama", t); bot.send_message(c, "✅", reply_markup=admin_menu())
        elif h == "reklama_instagram": cfg_set("reklama_instagram", t); bot.send_message(c, "✅", reply_markup=admin_menu())
        elif h == "reklama_telegram": cfg_set("reklama_telegram", t); bot.send_message(c, "✅", reply_markup=admin_menu())
        elif h == "reklama_vaqt":
            try:
                hh, mm = t.split(":"); int(hh); int(mm)
                cfg_set("reklama_vaqt", t); bot.send_message(c, f"✅ Vaqt: {t}", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Format: HH:MM")
        elif h == "soz_interval":
            try:
                s = int(t)
                if s < 60: raise ValueError
                cfg_set("soz_interval", str(s)); bot.send_message(c, f"✅ Interval: {s}s", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam (≥60)")
        elif h == "test_interval":
            try:
                s = int(t)
                if s < 60: raise ValueError
                cfg_set("test_interval", str(s)); bot.send_message(c, f"✅ Test interval: {s}s", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam (≥60)")
        elif h == "sovga_min":
            try: cfg_set("sovga_min", str(int(t))); bot.send_message(c, "✅", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam")
        elif h == "sovga_max":
            try: cfg_set("sovga_max", str(int(t))); bot.send_message(c, "✅", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam")
        elif h == "xabar_yuborish":
            y = 0
            r = db("SELECT user_id FROM users WHERE aktiv = 1", (), True)
            for row in r or []:
                try:
                    bot.send_message(row["user_id"], t, parse_mode='Markdown')
                    y += 1; time.sleep(0.05)
                except: pass
            bot.send_message(c, f"✅ Yuborildi: {y}", reply_markup=admin_menu())
        elif h == "ban_user":
            try:
                uid = int(t.strip()); u_upd(uid, aktiv=0)
                log_admin(m.chat.id, m.from_user.first_name, f"Ban: {uid}")
                bot.send_message(c, f"✅ Ban: {uid}", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam")
        elif h == "admin_qoshish":
            try:
                uid = int(t.strip())
                ADMINS.add(uid)
                db("INSERT OR IGNORE INTO admins (user_id, ism, sana) VALUES (?, ?, ?)",
                   (uid, "Admin", datetime.now().strftime("%d.%m.%Y %H:%M")))
                log_admin(m.chat.id, m.from_user.first_name, f"Admin qo'shdi: {uid}")
                bot.send_message(c, f"✅ Admin qo'shildi: {uid}", reply_markup=admin_menu())
                try:
                    bot.send_message(uid, "🎉 Siz admin qilindingiz!\n\n`/admin` yuboring.", parse_mode='Markdown')
                except: pass
            except: bot.send_message(c, "❌ Raqam kiriting!")
        elif h == "admin_ochirish":
            try:
                uid = int(t.strip())
                if uid == A:
                    bot.send_message(c, "❌ Asosiy adminni o'chirib bo'lmaydi!"); return
                ADMINS.discard(uid)
                db("DELETE FROM admins WHERE user_id = ?", (uid,))
                log_admin(m.chat.id, m.from_user.first_name, f"Admin o'chirdi: {uid}")
                bot.send_message(c, f"✅ Admin o'chirildi: {uid}", reply_markup=admin_menu())
            except: bot.send_message(c, "❌ Raqam kiriting!")
        ss(c, admin_holat=None)
        return

    if t == "📊 Statistika":
        bot.send_message(c, admin_statistika(), parse_mode='Markdown', reply_markup=admin_menu())
    elif t == "👥 Foydalanuvchilar":
        r = db("SELECT user_id, ism, familiya, ball FROM users ORDER BY ball DESC LIMIT 30", (), True)
        if not r:
            bot.send_message(c, "Bo'sh."); return
        txt = f"👥 *Foydalanuvchilar (TOP-30)*\n\n"
        for u in r:
            aktiv = "🟢" if (u_get(u["user_id"]) or {}).get("aktiv", 1) else "🔴"
            txt += f"{aktiv} {u.get('ism','?')} {u.get('familiya','')} — {u['ball']}\n"
        bot.send_message(c, txt, parse_mode='Markdown')
    elif t == "📢 Reklama sozlash":
        bot.send_message(c, "📢 *Reklama sozlamalari*", parse_mode='Markdown', reply_markup=rek_admin_menu())
    elif t == "✏️ Matn":
        ss(c, admin_holat="reklama_matn")
        bot.send_message(c, f"Hozirgi:\n\n{reklama_matn()}\n\nYangi matn:")
    elif t == "📸 Instagram":
        ss(c, admin_holat="reklama_instagram")
        bot.send_message(c, f"Hozirgi: {cfg_get('reklama_instagram')}\n\nYangi:")
    elif t == "💬 Telegram":
        ss(c, admin_holat="reklama_telegram")
        bot.send_message(c, f"Hozirgi: {cfg_get('reklama_telegram')}\n\nYangi:")
    elif t == "🔄 Avto reklama":
        hozir = cfg_get("reklama_auto", "1")
        yangi = "0" if hozir == "1" else "1"
        cfg_set("reklama_auto", yangi)
        holat = "✅ YOQILDI" if yangi == "1" else "❌ O'CHIRILDI"
        bot.send_message(c, holat, reply_markup=rek_admin_menu())
    elif t == "⏰ Reklama vaqti":
        ss(c, admin_holat="reklama_vaqt")
        bot.send_message(c, f"Hozirgi: {cfg_get('reklama_vaqt', '09:00')}\n\nYangi (HH:MM):")
    elif t == "👁 Ko'rish":
        bot.send_message(c, reklama_matn(), parse_mode='Markdown', reply_markup=reklama_btn())
    elif t == "📚 So'z sozlash":
        bot.send_message(c, "📚 *So'z sozlamalari*", parse_mode='Markdown', reply_markup=soz_admin_menu())
    elif t == "🔄 Avto so'z":
        hozir = cfg_get("soz_auto", "1")
        yangi = "0" if hozir == "1" else "1"
        cfg_set("soz_auto", yangi)
        holat = "✅ YOQILDI" if yangi == "1" else "❌ O'CHIRILDI"
        bot.send_message(c, holat, reply_markup=soz_admin_menu())
    elif t == "⏱ Interval":
        ss(c, admin_holat="soz_interval")
        bot.send_message(c, f"Hozirgi: {cfg_get('soz_interval', '300')}s\n\nYangi:")
    elif t == "🎯 Test sozlash":
        bot.send_message(c, "🎯 *Test sozlamalari*", parse_mode='Markdown', reply_markup=test_admin_menu())
    elif t == "🔄 Avto test":
        hozir = cfg_get("test_auto", "1")
        yangi = "0" if hozir == "1" else "1"
        cfg_set("test_auto", yangi)
        holat = "✅ YOQILDI" if yangi == "1" else "❌ O'CHIRILDI"
        bot.send_message(c, holat, reply_markup=test_admin_menu())
    elif t == "⏱ Test interval":
        ss(c, admin_holat="test_interval")
        bot.send_message(c, f"Hozirgi: {cfg_get('test_interval', '600')}s\n\nYangi:")
    elif t == "👁 Hozir yuborish":
        if not S:
            bot.send_message(c, "So'zlar yo'q."); return
        bugun = datetime.now().strftime("%d.%m.%Y")
        r = db("SELECT user_id FROM users WHERE oxirgi_kun = ?", (bugun,), True)
        y = 0
        for row in r or []:
            try:
                s = random.choice(S)
                bot.send_message(row["user_id"],
                                 f"📚 *Yangi so'z!*\n\n🇷🇺 *{s['ru']}*\n🇺🇿 _{s['uz']}_",
                                 parse_mode='Markdown', reply_markup=soz_bilaman_menu())
                y += 1; time.sleep(0.05)
            except: pass
        bot.send_message(c, f"✅ Yuborildi: {y}")
    elif t == "✉️ Xabar yuborish":
        ss(c, admin_holat="xabar_yuborish")
        bot.send_message(c, "✉️ Barcha foydalanuvchilarga xabar:")
    elif t == "📋 Talablar":
        r = db("SELECT user_id, matn, sana FROM talablar ORDER BY id DESC LIMIT 20", (), True)
        if not r:
            bot.send_message(c, "📭 Bo'sh."); return
        txt = f"📢 *Talablar: {len(r)}*\n\n"
        for i, t2 in enumerate(r, 1):
            u = u_get(t2["user_id"])
            ism = u.get("ism", "?") if u else "?"
            txt += f"{i}. {ism}:\n{t2['matn']}\n\n"
        bot.send_message(c, txt, parse_mode='Markdown')
    elif t == "🎁 Sovga sozlash":
        ss(c, admin_holat="sovga_min")
        bot.send_message(c, f"Hozir: min={cfg_get('sovga_min')}, max={cfg_get('sovga_max')}\n\nYangi min:")
    elif t == "🗑 Ban qilish":
        ss(c, admin_holat="ban_user")
        bot.send_message(c, "🗑 Ban qilish uchun user_id yuboring:")
    elif t == "🔐 Xavfsizlik":
        bot.send_message(c, "🔐 *Xavfsizlik*", parse_mode='Markdown', reply_markup=xavfsizlik_menu())
    elif t == "👥 Adminlar":
        txt = "👥 *Adminlar:*\n\n"
        for i, uid in enumerate(ADMINS, 1):
            u = u_get(uid)
            ism = u.get("ism", "?") if u else "?"
            marker = "👑 Asosiy" if uid == A else "🛡 Zaxira"
            txt += f"{i}. {marker} {ism} ({uid})\n"
        bot.send_message(c, txt, parse_mode='Markdown')
    elif t == "➕ Admin qo'shish":
        ss(c, admin_holat="admin_qoshish")
        bot.send_message(c, "➕ Yangi admin user_id:")
    elif t == "➖ Admin o'chirish":
        ss(c, admin_holat="admin_ochirish")
        bot.send_message(c, "➖ O'chiriladigan admin user_id:")
    elif t == "🔑 Parol ko'rish":
        bot.send_message(c, f"🔑 Parol: `{ADMIN_PASS}`", parse_mode='Markdown')
    elif t == "📜 Admin loglar":
        r = db("SELECT user_id, ism, amal, sana FROM admin_log ORDER BY id DESC LIMIT 20", (), True)
        if not r:
            bot.send_message(c, "📭 Bo'sh."); return
        txt = "📜 *Admin loglar:*\n\n"
        for i, row in enumerate(r, 1):
            txt += f"{i}. {row['ism']} — {row['amal']}\n📅 {row['sana']}\n\n"
        bot.send_message(c, txt, parse_mode='Markdown')
    elif t == "⬅️ Orqaga" or t == "⬅️ Chiqish":
        ss(c, admin_holat=None)
        bot.send_message(c, "👑 Admin panel", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("autotest_"))
def callback_autotest(call):
    try:
        parts = call.data.split("_", 2)
        uid = int(parts[1])
        javob = parts[2]
        if call.from_user.id != uid:
            bot.answer_callback_query(call.id, "❌ Bu test sizga tegishli emas!")
            return
        x = gs(str(uid))
        togri = x.get("auto_test_javob", "")
        if javob == togri:
            ball_qosh(uid, 5)
            bot.answer_callback_query(call.id, "✅ To'g'ri! +5 ball")
            try:
                bot.edit_message_text(f"✅ To'g'ri! +5 ball\n🏆 Jami: {ball_get(uid)}",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)
            except: pass
        else:
            bot.answer_callback_query(call.id, f"❌ To'g'ri: {togri}")
            try:
                bot.edit_message_text(f"❌ Noto'g'ri!\n\nTo'g'ri javob: {togri}",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)
            except: pass
        ss(str(uid), auto_test_javob=None)
    except Exception as e:
        log.error(f"Callback: {e}")

@bot.message_handler(func=lambda m: str(m.chat.id) != str(A) and m.chat.id not in ADMINS, content_types=['text'])
def hand(m):
    c = str(m.chat.id)
    t = m.text
    u = u_get(m.chat.id)
    if not u or not u.get("ism") or u.get("h"):
        return
    if u.get("aktiv", 1) == 0:
        return
    x = gs(c)

    if x.get("admin_parol"):
        if t == ADMIN_PASS:
            ADMINS.add(m.chat.id)
            db("INSERT OR IGNORE INTO admins (user_id, ism, sana) VALUES (?, ?, ?)",
               (m.chat.id, m.from_user.first_name or "?", datetime.now().strftime("%d.%m.%Y %H:%M")))
            log_admin(m.chat.id, m.from_user.first_name, "Admin bo'ldi")
            ss(c, admin_parol=False)
            bot.send_message(c, "✅ *Tasdiqlandi!*\n\n👑 Admin panel:",
                             parse_mode='Markdown', reply_markup=admin_menu())
            try:
                bot.send_message(A, f"🔐 *YANGI ADMIN*\n\n👤 {m.from_user.first_name}\n🆔 {m.chat.id}",
                                 parse_mode='Markdown')
            except: pass
        else:
            ss(c, admin_parol=False)
            bot.send_message(c, "❌ Noto'g'ri parol!")
        return

    if t == "✅ Bilaman":
        ball_qosh(m.chat.id, 2)
        ss(c, soz_yangi=None)
        bot.send_message(c, "✅ Zo'r! +2 ball", reply_markup=menu())
        return
    if t == "❌ Bilmadim":
        s = x.get("soz_yangi")
        if s:
            bot.send_message(c, f"🇷🇺 {s['ru']} — 🇺🇿 {s['uz']}", reply_markup=menu())
        else:
            bot.send_message(c, "Menyu:", reply_markup=menu())
        ss(c, soz_yangi=None)
        return

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
            ss(c, kundalik_gaplar=None)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return

    if x.get("talab"):
        if t == "⬅️ Orqaga":
            ss(c, talab=False, talab_yozish=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "📢 Talab yozish":
            ss(c, talab_yozish=True)
            bot.send_message(c, "📢 Talab yoki taklifingizni yozing:"); return
        if t == "📋 Mening talablarim":
            r = db("SELECT matn FROM talablar WHERE user_id = ? ORDER BY id DESC LIMIT 5", (m.chat.id,), True)
            if not r: bot.send_message(c, "Bo'sh.")
            else:
                txt = "📋 *Sizning talablaringiz:*\n\n"
                for i, x2 in enumerate(r, 1): txt += f"{i}. {x2['matn']}\n\n"
                bot.send_message(c, txt, parse_mode='Markdown')
            return
        if x.get("talab_yozish"):
            db("INSERT INTO talablar (user_id, matn, sana) VALUES (?, ?, ?)",
               (m.chat.id, t, datetime.now().strftime("%d.%m.%Y %H:%M")))
            bot.send_message(c, "✅ Rahmat!", reply_markup=menu())
            try: bot.send_message(A, f"📢 TALAB:\n{u.get('ism','?')}:\n{t}")
            except: pass
            ss(c, talab_yozish=False, talab=False); return

    if x.get("suhbat_kat"):
        if t == "🔊 Eshitish":
            kat = x["suhbat_kat"]; i = x.get("suhbat_i", 0)
            if i < len(SUHBAT_GAPLAR[kat]):
                gap = SUHBAT_GAPLAR[kat][i]["ru"]
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={gap}&tl=ru&client=tw-ob"
                    bot.send_voice(c, url)
                except: pass
            return
        if t == "➡️ Keyingi": ss(c, suhbat_i=x.get("suhbat_i", 0) + 1); suhbat_korsat(c); return
        if t == "⬅️ Oldingi": ss(c, suhbat_i=max(0, x.get("suhbat_i", 0) - 1)); suhbat_korsat(c); return
        if t == "⬅️ Orqaga":
            ss(c, suhbat_kat=None)
            bot.send_message(c, "Suhbat:", reply_markup=suh_menu()); return

    if x.get("suhbat"):
        if t == "⬅️ Orqaga":
            ss(c, suhbat=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in SUHBAT_GAPLAR:
            ss(c, suhbat_kat=t, suhbat_i=0); suhbat_korsat(c)
        return

    if x.get("gap"):
        if t == "⏹ To'xtatish":
            ss(c, gap=False)
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if t.strip().lower() == x.get("gap_togri", "").lower():
            ball_qosh(m.chat.id, 15)
            bot.send_message(c, "✅ To'g'ri! +15 ball")
            ss(c, gap=False)
            bot.send_message(c, "Menyu:", reply_markup=menu())
        else:
            bot.send_message(c, f"❌ To'g'ri: {x.get('gap_togri','')}")
        return

    if x.get("kat"):
        if t == "⬅️ Orqaga":
            ss(c, kat=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in KATEGORIYALAR:
            txt = f"📚 *{t}*\n\n"
            for i, rus in enumerate(KATEGORIYALAR[t], 1):
                for s in S:
                    if s["ru"] == rus:
                        txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
            bot.send_message(c, txt, parse_mode='Markdown')
        return

    if x.get("gram"):
        if t == "⬅️ Orqaga":
            ss(c, gram=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in GRAMMATIKA:
            bot.send_message(c, f"📖 *{t}*\n\n{GRAMMATIKA[t]}", parse_mode='Markdown')
        return

    if x.get("dost"):
        if t == "⬅️ Orqaga":
            ss(c, dost=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🔗 Havola":
            try:
                bi = bot.get_me()
                bot.send_message(c, f"🔗 *Havolangiz:*\n\n`https://t.me/{bi.username}?start={c}`\n\n+50 ball!",
                                 parse_mode='Markdown')
            except:
                bot.send_message(c, f"🔗 `https://t.me/Til_organ_uz_bot?start={c}`", parse_mode='Markdown')
        elif t == "👥 Do'stlarim":
            r = db("SELECT dost_id FROM dostlar WHERE user_id = ?", (m.chat.id,), True)
            if not r: bot.send_message(c, "Do'stlar yo'q.")
            else:
                txt = "👥 *Do'stlar:*\n\n"
                for i, row in enumerate(r, 1):
                    du = u_get(row["dost_id"])
                    ism = du.get("ism", "?") if du else "?"
                    ball = ball_get(row["dost_id"])
                    txt += f"{i}. {ism} — {ball}\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        return

    if x.get("talaffuz"):
        if t == "⏹ To'xtatish":
            ss(c, talaffuz=None)
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
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
        elif t == "➡️ Keyingi so'z":
            talaffuz(c)
        return

    if x.get("chat"):
        if t == "⬅️ Orqaga":
            ss(c, chat=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if x.get("chat_savol"):
            if TARJIMA_BOR:
                try:
                    n = GoogleTranslator(source='auto', target='ru').translate(t)
                    bot.send_message(c, f"🇷🇺 {n}")
                except: pass
            next_savol(c)
        return

    if x.get("oyin"):
        if t == "⏹ To'xtatish":
            ss(c, oyin=False)
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if x.get("oyin_javob"):
            togri = x["oyin_javob"]
            if t.lower().strip() == togri.lower().strip():
                ball_qosh(m.chat.id, 10)
                bot.send_message(c, "✅ To'g'ri! +10 ball")
                oyin_navbat(c)
            else:
                bot.send_message(c, f"❌ To'g'ri: {togri}")
                oyin_navbat(c)
            return

    if x.get("tarj"):
        if t == "⬅️ Orqaga":
            ss(c, tarj=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🇷🇺 → 🇺🇿":
            ss(c, tarj_til="ru-uz")
            bot.send_message(c, "✅ Ruscha → O'zbekcha."); return
        if t == "🇺🇿 → 🇷🇺":
            ss(c, tarj_til="uz-ru")
            bot.send_message(c, "✅ O'zbekcha → Ruscha."); return
        if TARJIMA_BOR:
            try:
                if x.get("tarj_til", "ru-uz") == "ru-uz":
                    n = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"🇷🇺 {t}\n\n🇺🇿 {n}")
                else:
                    n = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"🇺🇿 {t}\n\n🇷🇺 {n}")
            except: bot.send_message(c, "❌ Xato.")
        return

    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            ts = x.get("ts", 0) + 1; tt = x.get("tt", 0) + 1; ti = x.get("ti", 0) + 1
            ss(c, ts=ts, tt=tt, ti=ti)
            ball_qosh(m.chat.id, 5)
            bot.send_message(c, "✅ To'g'ri! +5 ball")
            test(c); return
        elif t in [s["uz"] for s in S]:
            tt = x.get("tt", 0) + 1; ti = x.get("ti", 0) + 1
            ss(c, tt=tt, ti=ti)
            bot.send_message(c, f"❌ To'g'ri: {x['ca']}")
            test(c); return

    if t == "📅 Kundalik":
        ball_qosh(m.chat.id, 1); kundalik_gaplar(c)
    elif t == "📚 Flashcard":
        cs(c); ss(c, a=True, i=0); flash(c)
    elif t == "🎯 Testlar":
        cs(c); ss(c, ta=True, ti=0, ts=0, tt=0, ca=None); test(c)
    elif t == "🎮 O'yin":
        cs(c); oyin_navbat(c)
    elif t == "💬 Suhbat":
        cs(c); ss(c, suhbat=True)
        bot.send_message(c, "💬 Suhbat:", reply_markup=suh_menu())
    elif t == "📝 Gap tuzish":
        gap_tuzish(c)
    elif t == "📚 Kategoriya":
        cs(c); ss(c, kat=True)
        bot.send_message(c, "📚 Kategoriya:", reply_markup=kat_menu())
    elif t == "🎵 Talaffuz":
        talaffuz(c)
    elif t == "🎁 Sovga":
        sovga(c)
    elif t == "👥 Do'stlar":
        cs(c); ss(c, dost=True)
        bot.send_message(c, "👥 Do'stlar:", reply_markup=dost_menu())
    elif t == "⭐ Sevimlilar":
        sevimlilar(c)
    elif t == "📖 Grammatika":
        cs(c); ss(c, gram=True)
        bot.send_message(c, "📖 Grammatika:", reply_markup=gram_menu())
    elif t == "💬 Chat":
        cs(c); next_savol(c)
    elif t == "📢 Talab va taklif":
        cs(c); ss(c, talab=True)
        bot.send_message(c, "📢 Talab:", reply_markup=tal_menu())
    elif t == "🏆 Reyting":
        bot.send_message(c, "🏆 Reyting:", reply_markup=rey_menu())
    elif t == "🥇 TOP-10":
        top10(c)
    elif t == "📊 Mening reytingim":
        mening_reyting(c)
    elif t == "🏅 Yutuqlarim":
        yutuqlarim(c)
    elif t == "📊 Grafik statistika":
        grafik(c)
    elif t == "📊 Statistika":
        ball = ball_get(c)
        u2 = u_get(c) or {}; streak = u2.get("streak", 0)
        bot.send_message(c, f"📊 *Statistika*\n\n📚 Jami: {len(S)}\n💬 Gaplar: {len(KUNDALIK_GAPLAR)}\n🏆 Ball: {ball}\n📊 {daraja(ball)}\n🔥 Streak: {streak} kun",
                         parse_mode='Markdown')
    elif t == "ℹ️ Yordam":
        bot.send_message(c, "📖 *Yordam*\n\n📅 Kundalik +1\n📚 Flashcard +2\n🎯 Testlar +5\n🎮 O'yin +10\n📝 Gap tuzish +15\n👥 Do'stlar +50\n🎁 Sovga\n🎵 Talaffuz\n📚 Kategoriya\n📖 Grammatika\n💬 Chat\n🔄 Tarjima",
                         parse_mode='Markdown')
    elif t == "🔄 Tarjima":
        cs(c); ss(c, tarj=True, tarj_til="ru-uz")
        bot.send_message(c, "🔄 Tarjima:", reply_markup=tarj_menu())
    elif t == "👁 Ko'rsatish":
        idx = x.get("i", 0)
        if idx < len(S):
            s = S[idx]
            bot.send_message(c, f"Tarjima:\n\n{s['ru']} → {s['uz']}", reply_markup=flash_btn())
    elif t == "🔊 Eshitish" and x.get("a"):
        idx = x.get("i", 0)
        if idx < len(S):
            s = S[idx]
            try:
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={s['ru']}&tl=ru&client=tw-ob"
                bot.send_voice(c, url)
            except: pass
    elif t == "✅ Bilaman" and x.get("a"):
        ball_qosh(m.chat.id, 2)
        s = x.get("s", 0) + 1; tt = x.get("t", 0) + 1; i = x.get("i", 0) + 1
        ss(c, s=s, t=tt, i=i); flash(c)
    elif t == "❌ Bilmayman" and x.get("a"):
        tt = x.get("t", 0) + 1; i = x.get("i", 0) + 1
        ss(c, t=tt, i=i); flash(c)
    elif t == "⭐ Saqlash":
        idx = x.get("i", 0)
        if idx < len(S):
            s = S[idx]
            try:
                db("INSERT OR IGNORE INTO sevimlilar (user_id, soz_ru) VALUES (?, ?)", (m.chat.id, s["ru"]))
                bot.send_message(c, "⭐ Saqlandi!")
            except:
                bot.send_message(c, "Allaqachon saqlangan.")
    elif t == "⏹ To'xtatish":
        ss(c, a=False); bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⏹ Testdan chiqish":
        ss(c, ta=False); bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⬅️ Orqaga":
        cs(c); bot.send_message(c, "Menyu:", reply_markup=menu())
    else:
        if TARJIMA_BOR and len(t) > 2:
            try:
                n = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"📝 Tarjima:\n\n🇷🇺 {t}\n\n🇺🇿 {n}")
                return
            except: pass
        bot.send_message(c, "Tugmalardan birini tanlang", reply_markup=menu())

if __name__ == "__main__":
    log.info("🚀 Bot ishga tushdi!")
    bot.remove_webhook()
    time.sleep(1)
    while True:
        try:
            bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            log.error(f"Polling: {e}")
            time.sleep(5)