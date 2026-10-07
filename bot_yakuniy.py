# -*- coding: utf-8 -*-
import os, json, time, random, re, logging
from threading import Thread, Lock
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

import telebot
from telebot import types

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# ==================== SOZLAMALAR ====================
# Render Environment'dan olinadi
T = os.environ.get("BOT_TOKEN", "")
A = int(os.environ.get("ADMIN_ID", 8178917212))

if not T:
    log.error("BOT_TOKEN topilmadi!")
    exit(1)

try:
    from deep_translator import GoogleTranslator
    TARJIMA_BOR = True
except ImportError:
    TARJIMA_BOR = False

# ==================== HEALTH SERVER ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a): pass

def run_health():
    port = int(os.environ.get("PORT", 8080))
    try:
        HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
        log.info(f"Health server: {port}")
    except Exception as e:
        log.error(f"Health: {e}")

Thread(target=run_health, daemon=True).start()

# ==================== BOT ====================
bot = telebot.TeleBot(T)
file_lock = Lock()

# ==================== MA'LUMOTLAR ====================
U, R, D, F, SV, TT = {}, {}, {}, {}, {}, {}
st = {}
S = []
kor = set()
KUNDALIK_GAPLAR = []

# So'zlar
for f in ["sozlar.json","sozlar_katta.json","sozlar_qoshimcha.json","sozlar_ish.json","sozlar_vaqt.json"]:
    if os.path.exists(f):
        try:
            with open(f, encoding="utf-8") as fp:
                d = json.load(fp)
            for s in d.get("sozlar", []):
                if s.get("ru") and s["ru"] not in kor:
                    S.append(s); kor.add(s["ru"])
            log.info(f"OK {f}: {len(d.get('sozlar', []))}")
        except Exception as e:
            log.error(f"{f}: {e}")

log.info(f"JAMI so'zlar: {len(S)}")

# Kundalik gaplar
for fname in ["kundalik_gaplar.json","kundalik_gaplar2.json"]:
    if os.path.exists(fname):
        try:
            with open(fname, encoding="utf-8") as fp:
                d = json.load(fp)
            KUNDALIK_GAPLAR.extend(d.get("gaplar", []))
            log.info(f"OK {fname}: {len(d.get('gaplar', []))}")
        except Exception as e:
            log.error(f"{fname}: {e}")

log.info(f"JAMI gaplar: {len(KUNDALIK_GAPLAR)}")

# Foydalanuvchi fayllari
for fname, var in [("users.json","U"),("reyting.json","R"),("kunlik.json","D"),
                   ("dostlar.json","F"),("sevimlilar.json","SV"),("talablar.json","TT")]:
    if os.path.exists(fname):
        try:
            with open(fname, encoding="utf-8") as fp:
                data = json.load(fp)
            if var == "U": U = data
            elif var == "R": R = data
            elif var == "D": D = data
            elif var == "F": F = data
            elif var == "SV": SV = data
            elif var == "TT": TT = data
        except Exception as e:
            log.error(f"{fname}: {e}")

# ==================== KONSTANTALAR ====================
REKLAMA_MATN = "📢 *Bizni kuzatib boring!*\n\n📸 Instagram: @odilov03_\n💬 Telegram: @odilov0_3"

def reklama_btn():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("📸 Instagram", url="https://instagram.com/odilov03_"),
        types.InlineKeyboardButton("💬 Telegram", url="https://t.me/odilov0_3")
    )
    return m

# ==================== ANTI-SPAM ====================
BLOK_SOZ = ["tucosprofit","tucosal","kanalni ko'rish","kanalni korish","join our channel",
            "must join","подпишись","подпишитесь","обязательно подпишись","реклама","продвижение",
            "промокод","заработок","заработать","криптовалюта","инвестиции","халява","скидка",
            "акция","успей","торопись","выигрыш","приз","лотерея","казино","ставки","букмекер",
            "обменник","бинарные опционы","форекс","инвестируй","получи доход"]

BLOK_LINK = ["t.me/tucosprofit","t.me/tucosal","t.me/joinchat","t.me/+","instagram.com/",
             "youtube.com/","youtu.be/","facebook.com/","tiktok.com/","whatsapp.com/","viber.com/"]

BOT_PAT = re.compile(r'@[a-zA-Z0-9_]+_?bot', re.IGNORECASE)
SPAM_HIST = {}

def matn_tekshir(matn):
    if not matn: return False, None
    ml = matn.lower()
    for soz in BLOK_SOZ:
        if soz.lower() in ml: return True, f"So'z: {soz}"
    for link in BLOK_LINK:
        if link.lower() in ml: return True, f"Link: {link}"
    if BOT_PAT.search(matn): return True, "Bot username"
    links = re.findall(r'https?://[^\s]+', matn)
    if len(links) >= 3: return True, f"Ko'p link"
    usernames = re.findall(r'@[a-zA-Z0-9_]+', matn)
    if len(usernames) >= 3: return True, f"Ko'p username"
    return False, None

def spam_tekshir(message):
    if message.forward_from or message.forward_from_chat or message.forward_sender_name:
        return True, "Forward"
    try:
        if message.forward_origin: return True, "Forward"
    except: pass
    if hasattr(message.from_user, 'is_bot') and message.from_user.is_bot:
        return True, "Bot"
    if message.reply_to_message and hasattr(message.reply_to_message.from_user, 'is_bot'):
        if message.reply_to_message.from_user.is_bot: return True, "Reply bot"
    if message.reply_markup and hasattr(message.reply_markup, 'inline_keyboard'):
        for row in message.reply_markup.inline_keyboard:
            for btn in row:
                if hasattr(btn, 'url') and btn.url:
                    for link in BLOK_LINK:
                        if link.lower() in btn.url.lower(): return True, f"Inline: {link}"
    if message.text:
        b, s = matn_tekshir(message.text)
        if b: return True, s
    if message.caption:
        b, s = matn_tekshir(message.caption)
        if b: return True, s
    if message.from_user:
        uid = message.from_user.id
        now = time.time()
        if uid not in SPAM_HIST: SPAM_HIST[uid] = []
        SPAM_HIST[uid] = [t for t in SPAM_HIST[uid] if now - t < 60]
        SPAM_HIST[uid].append(now)
        if len(SPAM_HIST[uid]) > 20: return True, "Rate limit"
    return False, None

# ==================== SUHBAT GAPLAR ====================
SUHBAT_GAPLAR = {
    "💼 Ishda": [
        {"ru":"Доброе утро!","uz":"Xayrli tong!"},
        {"ru":"Как ваши дела?","uz":"Ishlaringiz qanday?"},
        {"ru":"Что нового?","uz":"Nima yangilik?"},
        {"ru":"Я готов к работе.","uz":"Men ishga tayyorman."},
        {"ru":"Давайте начнём.","uz":"Keling, boshlaymiz."},
        {"ru":"Сколько времени?","uz":"Soat necha?"},
        {"ru":"Мне нужно закончить работу.","uz":"Ishni tugatishim kerak."},
        {"ru":"Хорошего дня!","uz":"Yaxshi kun tilayman!"},
        {"ru":"До завтра!","uz":"Ertagagacha!"},
        {"ru":"Спасибо за помощь.","uz":"Yordamingiz uchun rahmat."}
    ],
    "🚶 Ko'chada": [
        {"ru":"Извините, как пройти?","uz":"Kechirasiz, qanday boriladi?"},
        {"ru":"Где находится метро?","uz":"Metro qayerda?"},
        {"ru":"Это далеко?","uz":"Bu uzoqmi?"},
        {"ru":"Сколько стоит такси?","uz":"Taksi qancha turadi?"},
        {"ru":"Остановите здесь, пожалуйста.","uz":"Shu yerda to'xtating."},
        {"ru":"Я заблудился.","uz":"Men adashib qoldim."},
        {"ru":"Помогите, пожалуйста.","uz":"Yordam bering."},
        {"ru":"Где выход?","uz":"Chiqish qayerda?"},
        {"ru":"Спасибо большое!","uz":"Katta rahmat!"},
        {"ru":"До свидания!","uz":"Xayr!"}
    ],
    "🛒 Do'konda": [
        {"ru":"Сколько это стоит?","uz":"Bu qancha turadi?"},
        {"ru":"Это дорого.","uz":"Bu qimmat."},
        {"ru":"Есть дешевле?","uz":"Arzonroq bormi?"},
        {"ru":"Дайте, пожалуйста.","uz":"Bering, iltimos."},
        {"ru":"Можно картой?","uz":"Karta bilan bo'ladimi?"},
        {"ru":"Спасибо за покупку!","uz":"Rahmat!"},
        {"ru":"Где касса?","uz":"Kassa qayerda?"},
        {"ru":"Дайте чек, пожалуйста.","uz":"Chek bering."},
        {"ru":"Хорошего дня!","uz":"Yaxshi kun!"},
        {"ru":"Приходите ещё!","uz":"Yana keling!"}
    ],
    "☕ Suhbatda": [
        {"ru":"Привет! Как дела?","uz":"Salom! Qalaysiz?"},
        {"ru":"Меня зовут...","uz":"Mening ismim..."},
        {"ru":"Очень приятно!","uz":"Juda yoqimli!"},
        {"ru":"Откуда вы?","uz":"Qayerdansiz?"},
        {"ru":"Я из Узбекистана.","uz":"Men O'zbekistondanman."},
        {"ru":"Сколько вам лет?","uz":"Yoshingiz nechada?"},
        {"ru":"Что вы любите?","uz":"Nimani yaxshi ko'rasiz?"},
        {"ru":"Давайте встретимся.","uz":"Keling, uchrashamiz."},
        {"ru":"Какой у вас номер?","uz":"Raqamingiz qanday?"},
        {"ru":"До встречи!","uz":"Ko'rishguncha!"}
    ],
    "🏥 Shifokorda": [
        {"ru":"Мне плохо.","uz":"O'zimni yomon his qilyapman."},
        {"ru":"У меня болит голова.","uz":"Boshim og'riyapti."},
        {"ru":"У меня температура.","uz":"Haroratim bor."},
        {"ru":"Вызовите врача.","uz":"Shifokor chaqiring."},
        {"ru":"Где аптека?","uz":"Dorixona qayerda?"},
        {"ru":"Мне нужна помощь.","uz":"Menga yordam kerak."},
        {"ru":"Скорая помощь!","uz":"Tez yordam!"},
        {"ru":"Спасибо, доктор!","uz":"Rahmat, doktor!"}
    ],
    "📞 Telefonda": [
        {"ru":"Алло!","uz":"Allo!"},
        {"ru":"Кто это?","uz":"Bu kim?"},
        {"ru":"Можно...?","uz":"...mumkinmi?"},
        {"ru":"Позвоните позже.","uz":"Keyinroq qo'ng'iroq qiling."},
        {"ru":"Я перезвоню.","uz":"Men qayta qo'ng'iroq qilaman."},
        {"ru":"Не слышно.","uz":"Eshitilmayapti."},
        {"ru":"Говорите громче.","uz":"Balandroq gapiring."},
        {"ru":"До свидания!","uz":"Xayr!"}
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

# ==================== STATE ====================
def get_state(c):
    if c not in st:
        st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False,"ta":False}
    return st[c]

def set_state(c, **kw):
    x = get_state(c); x.update(kw); st[c] = x; return x

def clear_state(c):
    st[c] = {"i":0,"s":0,"t":0,"a":False,"tarj":False,"tarj_til":"ru-uz","oyin":False,"ta":False}

# ==================== SAQLASH ====================
def _save(data, fn):
    with file_lock:
        try:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"{fn}: {e}")

def saqlash(): _save(U, "users.json")
def reyting_saqlash(): _save(R, "reyting.json")
def kunlik_saqlash(): _save(D, "kunlik.json")
def dostlar_saqlash(): _save(F, "dostlar.json")
def sevimlilar_saqlash(): _save(SV, "sevimlilar.json")
def talablar_saqlash(): _save(TT, "talablar.json")

# ==================== YORDAMCHI ====================
def ball_qosh(uid, ball):
    R[str(uid)] = R.get(str(uid), 0) + ball
    reyting_saqlash()

def ism_tekshir(ism):
    if not ism or len(ism) < 2: return False
    if not re.match(r'^[\w\s\'-]{2,50}$', ism, re.UNICODE): return False
    if ism.strip().isdigit(): return False
    return True

def telefon_tekshir(tel):
    t = re.sub(r'[^\d+]', '', tel)
    return bool(re.match(r'^\+?\d{10,15}$', t))

def sana_tekshir(sana):
    try:
        d = datetime.strptime(sana, "%d.%m.%Y")
        return 5 <= (datetime.now().year - d.year) <= 120
    except: return False

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
    D[uid]["oxirgi_kun"] = bugun
    D[uid]["challenge"] = False
    D[uid]["sovga"] = False
    kunlik_saqlash(); return D[uid]["streak"]

def daraja(ball):
    if ball >= 5000: return "👑 C2"
    if ball >= 3000: return "🥇 C1"
    if ball >= 1500: return "🥈 B2"
    if ball >= 500: return "🥉 B1"
    if ball >= 100: return "📗 A2"
    return "📘 A1"

# ==================== MENYULAR ====================
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
    m.add("🔊 Eshitish","🔄 Yangilash","⬅️ Orqaga"); return m

def suhbat_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in SUHBAT_GAPLAR.keys(): m.add(k)
    m.add("⬅️ Orqaga"); return m

def flash_btn():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👁 Ko'rsatish","✅ Bilaman","❌ Bilmayman","⭐ Saqlash")
    m.add("🔊 Eshitish","⏹ To'xtatish"); return m

def tarjima_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇷🇺 Ruscha → 🇺🇿 O'zbekcha","🇺🇿 O'zbekcha → 🇷🇺 Ruscha","⬅️ Orqaga"); return m

def reyting_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🥇 TOP-10","📊 Mening reytingim","🏅 Yutuqlarim")
    m.add("📊 Grafik statistika","⬅️ Orqaga"); return m

def kategoriya_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in KATEGORIYALAR.keys(): m.add(k)
    m.add("⬅️ Orqaga"); return m

def dost_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("🔗 Havola","👥 Do'stlarim","🏆 Do'stlar reytingi","⬅️ Orqaga"); return m

def gram_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for k in GRAMMATIKA.keys(): m.add(k)
    m.add("⬅️ Orqaga"); return m

def talab_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("📢 Talab/taklif yozish","📋 Mening talablarim","⬅️ Orqaga"); return m

def gap_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("⏹ To'xtatish"); return m

# ==================== YORDAMCHI FUNKSIYALAR ====================
def kundalik_gaplar(c):
    if not KUNDALIK_GAPLAR:
        bot.send_message(c, "Gaplar yo'q."); return
    gaplar = random.sample(KUNDALIK_GAPLAR, min(10, len(KUNDALIK_GAPLAR)))
    txt = f"💬 *Kundalik gaplar*\n📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    for i, g in enumerate(gaplar, 1):
        txt += f"*{i}.* 🇷🇺 {g['ru']}\n     🇺🇿 _{g['uz']}_\n\n"
    txt += f"🏆 Jami: {R.get(c, 0)}\n📚 Jami: {len(KUNDALIK_GAPLAR)} ta"
    set_state(c, kundalik_gaplar=gaplar)
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=kundalik_menu())

def suhbat_korsat(c):
    x = get_state(c)
    kat = x.get("suhbat_kat"); i = x.get("suhbat_i", 0)
    if not kat: return
    gaplar = SUHBAT_GAPLAR[kat]
    if i >= len(gaplar):
        set_state(c, suhbat_kat=None)
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    gap = gaplar[i]
    txt = f"💬 *{kat}* ({i+1}/{len(gaplar)})\n\n🇷🇺 *{gap['ru']}*\n\n🇺🇿 {gap['uz']}"
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    mk.add("🔊 Eshitish","⬅️ Oldingi","➡️ Keyingi"); mk.add("⬅️ Orqaga")
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=mk)

def next_savol(c):
    savol = random.choice(CHAT_SAVOLLAR)
    set_state(c, chat=True, chat_savol=savol)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⬅️ Orqaga")
    bot.send_message(c, f"💬 *Chat*\n\n{savol['savol']}\n\n_Ruscha javob yozing_\n💡 {savol['javob']}",
                     parse_mode='Markdown', reply_markup=mk)

def gap_tuzish(c):
    g = random.choice(GAPLAR)
    sozlar = g["sozlar"].copy(); random.shuffle(sozlar)
    st[c] = {"gap":True,"gap_togri":g["togri"]}
    txt = "📝 *Gap tuzish*\n\nSo'zlardan gap tuzing:\n\n"
    for s in sozlar: txt += f"• {s}\n"
    txt += f"\n💡 _{g['tarjima']}_\n🎁 +15 ball"
    bot.send_message(c, txt, parse_mode='Markdown', reply_markup=gap_menu())

def sovga(c):
    uid = str(c); bugun = datetime.now().strftime("%d.%m.%Y")
    if uid not in D: D[uid] = {"oxirgi_kun":bugun,"streak":1,"challenge":False,"sovga":False}
    if D[uid].get("sovga"):
        bot.send_message(c, "Bugungi sovgani oldingiz!", reply_markup=menu()); return
    ball = random.choice([10,20,30,50,100])
    ball_qosh(c, ball)
    D[uid]["sovga"] = True; kunlik_saqlash()
    bot.send_message(c, f"🎁 *Sovga!*\n\n+{ball} ball!\n🏆 Jami: {R.get(c,0)}",
                     parse_mode='Markdown', reply_markup=menu())

def talaffuz(c):
    if not S: return
    s = random.choice(S)
    st[c] = {"talaffuz":s}
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("🔊 Eshitish","👁 Tarjima","➡️ Keyingi so'z","⏹ To'xtatish")
    bot.send_message(c, f"🎵 *Talaffuz*\n\nRuscha: *{s['ru']}*", parse_mode='Markdown', reply_markup=mk)

def yutuqlarim(c):
    uid = str(c); ball = R.get(uid, 0); streak = D.get(uid, {}).get("streak", 0)
    dostlar = len(F.get(uid, []))
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
    ball = R.get(str(c), 0)
    txt = "📊 *Grafik*\n\n"
    for d in [0, 100, 500, 1500, 3000, 5000]:
        txt += f"{'✅' if ball >= d else '⬜'} {d} ball\n"
    txt += f"\n🏆 Siz: {ball}\n📊 {daraja(ball)}"
    bot.send_message(c, txt, parse_mode='Markdown')

def sevimlilar(c):
    uid = str(c)
    if uid not in SV or not SV[uid]:
        bot.send_message(c, "⭐ Bo'sh."); return
    txt = "⭐ *Sevimlilar:*\n\n"
    for i, rus in enumerate(SV[uid], 1):
        for s in S:
            if s["ru"] == rus:
                txt += f"{i}. {s['ru']} — {s['uz']}\n"; break
    bot.send_message(c, txt, parse_mode='Markdown')

def top10(c):
    if not R:
        bot.send_message(c, "🏆 Bo'sh."); return
    sar = sorted(R.items(), key=lambda x: x[1], reverse=True)[:10]
    txt = "🏆 *TOP-10*\n\n"
    med = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, (uid, ball) in enumerate(sar):
        ism = U.get(uid, {}).get("ism", "?")
        txt += f"{med[i]} {ism} — {ball}\n"
    bot.send_message(c, txt, parse_mode='Markdown')

def mening_reyting(c):
    ball = R.get(str(c), 0)
    orin = 1
    if R:
        sar = sorted(R.items(), key=lambda x: x[1], reverse=True)
        for i, (uid, _) in enumerate(sar, 1):
            if uid == str(c): orin = i; break
    streak = D.get(c, {}).get("streak", 0)
    bot.send_message(c, f"📊 *Reytingingiz*\n\n🏆 Ball: *{ball}*\n📍 O'rin: *{orin}* / {len(R)}\n📊 {daraja(ball)}\n🔥 Streak: {streak} kun",
                     parse_mode='Markdown')

def flash(c):
    x = get_state(c); idx = x.get("i",0)
    if not S or idx >= len(S):
        bot.send_message(c, "Tugadi!", reply_markup=menu()); return
    s = S[idx]
    bot.send_message(c, f"Flashcard ({idx+1}/{len(S)})\n\nRuscha: {s['ru']}", reply_markup=flash_btn())

def test(c):
    x = get_state(c); idx = x.get("ti",0)
    if not S or idx >= len(S):
        sc = x.get("ts",0); tt = x.get("tt",0)
        x["ta"] = False; st[c] = x
        bot.send_message(c, f"Tugadi!\n\nJami: {tt}\nTo'g'ri: {sc}", reply_markup=menu()); return
    tg = S[idx]
    bs = [s for s in S if s["uz"] != tg["uz"]]
    if len(bs) < 3:
        bot.send_message(c, "So'zlar kam."); return
    nt = random.sample(bs, 3); vr = [tg] + nt; random.shuffle(vr)
    x["ca"] = tg["uz"]; st[c] = x
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for v in vr: mk.add(v["uz"])
    mk.add("⏹ Testdan chiqish")
    bot.send_message(c, f"Test ({idx+1}/{len(S)})\n\n{tg['ru']} - ?", reply_markup=mk)

def oyin_navbat(c):
    if len(S) < 4:
        bot.send_message(c, "So'zlar kam.", reply_markup=menu()); return
    s = random.choice(S)
    set_state(c, oyin_javob=s["uz"], oyin=True)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.add("⏹ To'xtatish")
    bot.send_message(c, f"🎮 *O'yin*\n\nRuscha: *{s['ru']}*\n\nTarjima yozing\n🎁 +10 ball",
                     parse_mode='Markdown', reply_markup=mk)

# ==================== REKLAMA (FAQAT BIR MARTA) ====================
_reklama_started = False

def reklama_yubor():
    global _reklama_started
    if _reklama_started:
        return
    _reklama_started = True
    while True:
        time.sleep(3600)
        try:
            for uid in list(U.keys()):
                try:
                    bot.send_message(int(uid), REKLAMA_MATN, parse_mode='Markdown', reply_markup=reklama_btn())
                    time.sleep(0.1)
                except: pass
        except Exception as e:
            log.error(f"Reklama: {e}")

Thread(target=reklama_yubor, daemon=True).start()

# ==================== HAFTALIK ====================
def haftalik():
    while True:
        try:
            h = datetime.now()
            if h.weekday() == 0 and h.hour == 9:
                sar = sorted(R.items(), key=lambda x: x[1], reverse=True)[:3]
                for i, (uid, _) in enumerate(sar):
                    bonus = [100, 50, 25][i]
                    ball_qosh(uid, bonus)
                    try: bot.send_message(int(uid), f"🎉 Haftalik bonus: +{bonus} ball!")
                    except: pass
            time.sleep(3600)
        except Exception as e:
            log.error(f"Haftalik: {e}"); time.sleep(3600)

Thread(target=haftalik, daemon=True).start()

# ==================== HANDLERLAR ====================
@bot.message_handler(commands=['start'])
def start(m):
    c = str(m.chat.id)
    if m.chat.id == A:
        bot.send_message(c, "👑 Admin\n\n/royxat\n/talablar"); return
    # Referal
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
        except: pass
    if c in U and U[c].get("ism"):
        streak = kunlik_tekshir(m.chat.id)
        ball_qosh(m.chat.id, 1)
        clear_state(c)
        bot.send_message(c, f"Salom, {U[c]['ism']}! 👋\n\n📚 {len(S)} so'z\n💬 {len(KUNDALIK_GAPLAR)} gap\n🔥 Streak: {streak}\n🏆 Ball: {R.get(c,0)}\n🎁 +1 ball!",
                         reply_markup=menu())
        try: bot.send_message(c, REKLAMA_MATN, parse_mode='Markdown', reply_markup=reklama_btn())
        except: pass
        return
    U[c] = {"id":m.chat.id,"ism":"","familiya":"","sana_tugilgan":"","tel":"",
            "h":"ism","sana":datetime.now().strftime("%d.%m.%Y %H:%M")}
    saqlash()
    bot.send_message(c, "🌍 Assalomu alaykum!\n\n📝 Ismingizni kiriting:",
                     reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['royxat'])
def royxat(m):
    if m.chat.id != A: return
    txt = f"👥 Foydalanuvchilar: {len(U)}\n\n"
    for uid, u in list(U.items())[:30]:
        txt += f"• {u.get('ism','?')} {u.get('familiya','')} — {R.get(uid,0)} ball\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(commands=['talablar'])
def talablar_admin(m):
    if m.chat.id != A: return
    if not TT:
        bot.send_message(m.chat.id, "📭 Yo'q."); return
    txt = f"📢 Talablar: {len(TT)}\n\n"
    for i, (uid, talab) in enumerate(list(TT.items())[-20:], 1):
        ism = U.get(uid, {}).get("ism", "?")
        txt += f"{i}. {ism}:\n{talab['matn']}\n\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: str(m.chat.id) in U and U[str(m.chat.id)].get("h"))
def reg(m):
    if not m.text:
        bot.send_message(m.chat.id, "Iltimos, matn yuboring."); return
    c = str(m.chat.id); u = U[c]; t = m.text.strip()
    if u["h"] == "ism":
        if not ism_tekshir(t):
            bot.send_message(c, "❌ Ism noto'g'ri!\nKamida 2 harf.\nQaytadan:"); return
        u["ism"] = t; u["h"] = "fam"; saqlash()
        bot.send_message(c, "✅ Familiyangizni kiriting:")
    elif u["h"] == "fam":
        if not ism_tekshir(t):
            bot.send_message(c, "❌ Familiya noto'g'ri!\nQaytadan:"); return
        u["familiya"] = t; u["h"] = "sana"; saqlash()
        bot.send_message(c, "✅ Tug'ilgan sana:\n\nFormat: DD.MM.YYYY")
    elif u["h"] == "sana":
        if not sana_tekshir(t):
            bot.send_message(c, "❌ Sana noto'g'ri!\nFormat: DD.MM.YYYY\nMasalan: 15.05.1995"); return
        u["sana_tugilgan"] = t; u["h"] = "tel"; saqlash()
        bot.send_message(c, "✅ Telefon:\n\nFormat: +998901234567")
    elif u["h"] == "tel":
        if not telefon_tekshir(t):
            bot.send_message(c, "❌ Telefon noto'g'ri!\nFormat: +998901234567"); return
        u["tel"] = t; u["h"] = ""; saqlash()
        ball_qosh(m.chat.id, 5); kunlik_tekshir(m.chat.id)
        bot.send_message(c, f"🎉 Rahmat, {u['ism']}!\n🎁 +5 ball!")
        try: bot.send_message(c, REKLAMA_MATN, parse_mode='Markdown', reply_markup=reklama_btn())
        except: pass
        try: bot.send_message(A, f"👤 YANGI:\n{u['ism']} {u['familiya']}\n{u['sana_tugilgan']}\n{u['tel']}")
        except: pass
        clear_state(c)
        bot.send_message(c, "Menyu:", reply_markup=menu())

@bot.message_handler(func=lambda m: True, content_types=['text'])
def hand(m):
    c = str(m.chat.id); t = m.text
    if m.chat.id == A: return
    if c not in U or not U[c].get("ism") or U[c].get("h"): return

    # ANTI-SPAM
    if m.from_user and m.from_user.id != A:
        blok, sabab = spam_tekshir(m)
        if blok:
            try: bot.send_message(A, f"🚫 SPAM\n👤 {m.from_user.first_name}\n📛 {sabab}")
            except: pass
            try: bot.send_message(c, f"🚫 Xabar bloklandi.\nSabab: {sabab}")
            except: pass
            return

    x = get_state(c)

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
            set_state(c, kundalik_gaplar=None)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return

    if x.get("talab"):
        if t == "⬅️ Orqaga":
            set_state(c, talab=False, talab_yozish=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "📢 Talab/taklif yozish":
            set_state(c, talab_yozish=True)
            bot.send_message(c, "📢 Talab yoki taklifingizni yozing:"); return
        if t == "📋 Mening talablarim":
            bot.send_message(c, TT.get(c, {}).get("matn", "Yo'q")); return
        if x.get("talab_yozish"):
            TT[c] = {"matn": t, "sana": datetime.now().strftime("%d.%m.%Y %H:%M")}
            talablar_saqlash()
            bot.send_message(c, "✅ Rahmat!", reply_markup=menu())
            try: bot.send_message(A, f"📢 TALAB:\n{U[c].get('ism','?')}:\n{t}")
            except: pass
            set_state(c, talab_yozish=False, talab=False); return

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
        if t == "➡️ Keyingi":
            set_state(c, suhbat_i=x.get("suhbat_i", 0) + 1); suhbat_korsat(c); return
        if t == "⬅️ Oldingi":
            set_state(c, suhbat_i=max(0, x.get("suhbat_i", 0) - 1)); suhbat_korsat(c); return
        if t == "⬅️ Orqaga":
            set_state(c, suhbat_kat=None)
            bot.send_message(c, "Suhbat:", reply_markup=suhbat_menu()); return

    if x.get("suhbat"):
        if t == "⬅️ Orqaga":
            set_state(c, suhbat=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in SUHBAT_GAPLAR:
            set_state(c, suhbat_kat=t, suhbat_i=0); suhbat_korsat(c)
        return

    if x.get("gap"):
        if t == "⏹ To'xtatish":
            set_state(c, gap=False)
            bot.send_message(c, "To'xtatildi.", reply_markup=menu()); return
        if t.strip().lower() == x.get("gap_togri","").lower():
            ball_qosh(m.chat.id, 15)
            bot.send_message(c, "✅ To'g'ri! +15 ball")
            set_state(c, gap=False)
            bot.send_message(c, "Menyu:", reply_markup=menu())
        else:
            bot.send_message(c, f"❌ To'g'ri: {x.get('gap_togri','')}")
        return

    if x.get("kat"):
        if t == "⬅️ Orqaga":
            set_state(c, kat=False)
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
            set_state(c, gram=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t in GRAMMATIKA:
            bot.send_message(c, f"📖 *{t}*\n\n{GRAMMATIKA[t]}", parse_mode='Markdown')
        return

    if x.get("dost"):
        if t == "⬅️ Orqaga":
            set_state(c, dost=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🔗 Havola":
            bot.send_message(c, f"🔗 *Havolangiz:*\n\n`https://t.me/Til_organ_uz_bot?start={c}`\n\n+50 ball!",
                             parse_mode='Markdown')
        elif t == "👥 Do'stlarim":
            d = F.get(c, [])
            if not d: bot.send_message(c, "Do'stlar yo'q.")
            else:
                txt = "👥 *Do'stlar:*\n\n"
                for i, u in enumerate(d, 1):
                    txt += f"{i}. {U.get(u,{}).get('ism','?')} — {R.get(u,0)}\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        elif t == "🏆 Do'stlar reytingi":
            d = F.get(c, [])
            if not d: bot.send_message(c, "Do'stlar yo'q.")
            else:
                bl = [(u, R.get(u,0)) for u in d + [c]]
                bl.sort(key=lambda x: x[1], reverse=True)
                txt = "🏆 *Do'stlar:*\n\n"
                for i, (u, b) in enumerate(bl, 1):
                    ism = U.get(u,{}).get("ism","?") if u != c else "Siz"
                    txt += f"{i}. {ism} — {b}\n"
                bot.send_message(c, txt, parse_mode='Markdown')
        return

    if x.get("talaffuz"):
        if t == "⏹ To'xtatish":
            set_state(c, talaffuz=None)
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
            set_state(c, chat=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if x.get("chat_savol"):
            if TARJIMA_BOR:
                try:
                    natija = GoogleTranslator(source='auto', target='ru').translate(t)
                    bot.send_message(c, f"🇷🇺 {natija}")
                except: pass
            next_savol(c)
        return

    if x.get("oyin"):
        if t == "⏹ To'xtatish":
            set_state(c, oyin=False)
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
            set_state(c, tarj=False)
            bot.send_message(c, "Menyu:", reply_markup=menu()); return
        if t == "🇷🇺 Ruscha → 🇺🇿 O'zbekcha":
            set_state(c, tarj_til="ru-uz")
            bot.send_message(c, "✅ Ruscha → O'zbekcha."); return
        if t == "🇺🇿 O'zbekcha → 🇷🇺 Ruscha":
            set_state(c, tarj_til="uz-ru")
            bot.send_message(c, "✅ O'zbekcha → Ruscha."); return
        if TARJIMA_BOR:
            try:
                if x["tarj_til"] == "ru-uz":
                    n = GoogleTranslator(source='ru', target='uz').translate(t)
                    bot.send_message(c, f"🇷🇺 {t}\n\n🇺🇿 {n}")
                else:
                    n = GoogleTranslator(source='uz', target='ru').translate(t)
                    bot.send_message(c, f"🇺🇿 {t}\n\n🇷🇺 {n}")
            except: bot.send_message(c, "❌ Tarjima xatosi.")
        return

    if x.get("ta") and x.get("ca"):
        if t == x["ca"]:
            x["ts"] = x.get("ts",0)+1; x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; ball_qosh(m.chat.id, 5)
            bot.send_message(c, "✅ To'g'ri! +5 ball"); test(c); return
        elif t in [s["uz"] for s in S]:
            x["tt"] = x.get("tt",0)+1; x["ti"] = x.get("ti",0)+1
            st[c] = x; bot.send_message(c, f"❌ To'g'ri: {x['ca']}"); test(c); return

    # ===== MENYU =====
    if t == "📅 Kundalik":
        ball_qosh(m.chat.id, 1); kundalik_gaplar(c)
    elif t == "📚 Flashcard":
        clear_state(c); set_state(c, a=True); flash(c)
    elif t == "🎯 Testlar":
        clear_state(c); set_state(c, ta=True, ti=0, ts=0, tt=0, ca=None); test(c)
    elif t == "🎮 O'yin":
        clear_state(c); oyin_navbat(c)
    elif t == "💬 Suhbat":
        clear_state(c); set_state(c, suhbat=True)
        bot.send_message(c, "💬 Suhbat:", reply_markup=suhbat_menu())
    elif t == "📝 Gap tuzish":
        gap_tuzish(c)
    elif t == "📚 Kategoriya":
        clear_state(c); set_state(c, kat=True)
        bot.send_message(c, "📚 Kategoriya:", reply_markup=kategoriya_menu())
    elif t == "🎵 Talaffuz":
        talaffuz(c)
    elif t == "🎁 Sovga":
        sovga(c)
    elif t == "👥 Do'stlar":
        clear_state(c); set_state(c, dost=True)
        bot.send_message(c, "👥 Do'stlar:", reply_markup=dost_menu())
    elif t == "⭐ Sevimlilar":
        sevimlilar(c)
    elif t == "📖 Grammatika":
        clear_state(c); set_state(c, gram=True)
        bot.send_message(c, "📖 Grammatika:", reply_markup=gram_menu())
    elif t == "💬 Chat":
        clear_state(c); next_savol(c)
    elif t == "📢 Talab va taklif":
        clear_state(c); set_state(c, talab=True)
        bot.send_message(c, "📢 Talab:", reply_markup=talab_menu())
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
    elif t == "📊 Statistika":
        ball = R.get(c, 0); streak = D.get(c, {}).get("streak", 0)
        bot.send_message(c, f"📊 *Statistika*\n\n📚 Jami: {len(S)}\n💬 Gaplar: {len(KUNDALIK_GAPLAR)}\n🏆 Ball: {ball}\n📊 {daraja(ball)}\n🔥 Streak: {streak} kun",
                         parse_mode='Markdown')
    elif t == "ℹ️ Yordam":
        bot.send_message(c, "📖 *Yordam*\n\n📅 Kundalik +1\n📚 Flashcard +2\n🎯 Testlar +5\n🎮 O'yin +10\n📝 Gap tuzish +15\n👥 Do'stlar +50\n🎁 Sovga\n🎵 Talaffuz\n📚 Kategoriya\n📖 Grammatika\n💬 Chat\n🔄 Tarjima",
                         parse_mode='Markdown')
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
    elif t == "✅ Bilaman":
        ball_qosh(m.chat.id, 2)
        x["s"] = x.get("s",0)+1; x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "❌ Bilmayman":
        x["t"] = x.get("t",0)+1; x["i"] = x.get("i",0)+1
        st[c] = x; flash(c)
    elif t == "⭐ Saqlash":
        idx = x.get("i", 0)
        if idx < len(S):
            s = S[idx]; uid = str(c)
            if uid not in SV: SV[uid] = []
            if s["ru"] not in SV[uid]:
                SV[uid].append(s["ru"]); sevimlilar_saqlash()
                bot.send_message(c, "⭐ Saqlandi!")
            else:
                bot.send_message(c, "Allaqachon saqlangan.")
    elif t == "⏹ To'xtatish":
        set_state(c, a=False)
        bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⏹ Testdan chiqish":
        set_state(c, ta=False)
        bot.send_message(c, "To'xtatildi.", reply_markup=menu())
    elif t == "⬅️ Orqaga":
        clear_state(c)
        bot.send_message(c, "Menyu:", reply_markup=menu())
    else:
        if TARJIMA_BOR and len(t) > 2:
            try:
                n = GoogleTranslator(source='auto', target='uz').translate(t)
                bot.send_message(c, f"📝 Tarjima:\n\n🇷🇺 {t}\n\n🇺🇿 {n}")
                return
            except: pass
        bot.send_message(c, "Tugmalardan birini tanlang", reply_markup=menu())

# ==================== ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    log.info("🚀 Bot ishga tushdi...")
    bot.remove_webhook()
    time.sleep(1)
    while True:
        try:
            bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            log.error(f"Polling xato: {e}")
            time.sleep(5)