"""
Anti-Spam va Anti-Bot himoya moduli
Boshqa botlardan keladigan har qanday xabarni bloklaydi
"""

import re
import time
from datetime import datetime, timedelta

# ===== BLOKLANGAN SO'ZLAR =====
BLOKLANGAN_SOZLAR = [
    "tucosprofit",
    "tucosalаmanca",
    "tucosal",
    "premium",
    "kanalni ko'rish",
    "kanalni korish",
    "join our channel",
    "to use this bot",
    "must join",
    "подключит",
    "подпишись",
    "подпишитесь",
    "обязательно",
    "реклама",
    "рекламный",
    "продвижение",
    "промокод",
    "бесплатно",
    "заработок",
    "заработать",
    "криптовалюта",
    "инвестиции",
    "халява",
    "скидка",
    "акция",
    "только сегодня",
    "успей",
    "торопись",
    "выигрыш",
    "приз",
    "лотерея",
    "казино",
    "ставки",
    "букмекер",
]

# ===== BLOKLANGAN LINKLAR =====
BLOKLANGAN_LINKLAR = [
    "t.me/tucosprofit",
    "t.me/tucosal",
    "t.me/joinchat",
    "t.me/+",
    "instagram.com/",
    "youtube.com/",
    "youtu.be/",
    "facebook.com/",
    "tiktok.com/",
    "whatsapp.com/",
    "viber.com/",
]

# ===== BOT USERNAME'LAR =====
BOT_USERNAME_PATTERN = re.compile(r'@[a-zA-Z0-9_]+_?bot', re.IGNORECASE)

# ===== SPAM HISTORY =====
SPAM_HISTORY = {}  # {user_id: [timestamps]}

def matn_tekshir(matn):
    """Matnni spam uchun tekshiradi"""
    if not matn:
        return False, None
    
    matn_lower = matn.lower()
    
    # 1. Bloklangan so'zlarni tekshirish
    for soz in BLOKLANGAN_SOZLAR:
        if soz.lower() in matn_lower:
            return True, f"Bloklangan so'z: {soz}"
    
    # 2. Bloklangan linklarni tekshirish
    for link in BLOKLANGAN_LINKLAR:
        if link.lower() in matn_lower:
            return True, f"Bloklangan link: {link}"
    
    # 3. Bot username larni tekshirish
    if BOT_USERNAME_PATTERN.search(matn):
        return True, "Bot username topildi"
    
    # 4. Telegram linklarni tekshirish (@username)
    if re.search(r'@[a-zA-Z0-9_]{5,}', matn):
        # Faqat kanal/guruh linklari (bot emas)
        if "t.me/" in matn_lower or "telegram.me/" in matn_lower:
            return True, "Telegram link"
    
    # 5. Ko'p linklar (3+)
    linklar = re.findall(r'https?://[^\s]+', matn)
    if len(linklar) >= 3:
        return True, f"Ko'p linklar: {len(linklar)}"
    
    # 6. Ko'p @username lar (3+)
    usernames = re.findall(r'@[a-zA-Z0-9_]+', matn)
    if len(usernames) >= 3:
        return True, f"Ko'p username: {len(usernames)}"
    
    return False, None

def forward_tekshir(message):
    """Forward xabarni tekshiradi"""
    # Forward manbasi
    if message.forward_from:
        return True, f"Forward: {message.forward_from.first_name}"
    
    if message.forward_from_chat:
        return True, f"Forward chat: {message.forward_from_chat.title}"
    
    if message.forward_sender_name:
        return True, f"Forward: {message.forward_sender_name}"
    
    # Forward origin (yangi API)
    try:
        if message.forward_origin:
            return True, "Forward origin"
    except:
        pass
    
    return False, None

def bot_tekshir(message):
    """Botdan kelgan xabarni tekshiradi"""
    # Xabar yuborgan bot
    if hasattr(message.from_user, 'is_bot') and message.from_user.is_bot:
        return True, f"Bot: @{message.from_user.username}"
    
    # Reply qilingan bot
    if message.reply_to_message:
        if hasattr(message.reply_to_message.from_user, 'is_bot') and message.reply_to_message.from_user.is_bot:
            return True, f"Reply botga"
    
    return False, None

def inline_tekshir(message):
    """Inline tugmalarni tekshiradi"""
    if message.reply_markup:
        # InlineKeyboardMarkup
        if hasattr(message.reply_markup, 'inline_keyboard'):
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if hasattr(button, 'url') and button.url:
                        for link in BLOKLANGAN_LINKLAR:
                            if link.lower() in button.url.lower():
                                return True, f"Inline link: {button.url}"
    return False, None

def spam_tekshir(message):
    """Xabarni to'liq tekshiradi"""
    user_id = message.from_user.id if message.from_user else None
    
    # 1. Forward
    blok, sabab = forward_tekshir(message)
    if blok:
        return True, sabab
    
    # 2. Bot
    blok, sabab = bot_tekshir(message)
    if blok:
        return True, sabab
    
    # 3. Inline
    blok, sabab = inline_tekshir(message)
    if blok:
        return True, sabab
    
    # 4. Matn
    if message.text:
        blok, sabab = matn_tekshir(message.text)
        if blok:
            return True, sabab
    
    # 5. Caption (rasm ostidagi matn)
    if message.caption:
        blok, sabab = matn_tekshir(message.caption)
        if blok:
            return True, sabab
    
    # 6. Rate limit (1 daqiqada 20+ xabar)
    if user_id:
        hozir = time.time()
        if user_id not in SPAM_HISTORY:
            SPAM_HISTORY[user_id] = []
        SPAM_HISTORY[user_id] = [t for t in SPAM_HISTORY[user_id] if hozir - t < 60]
        SPAM_HISTORY[user_id].append(hozir)
        
        if len(SPAM_HISTORY[user_id]) > 20:
            return True, f"Rate limit: {len(SPAM_HISTORY[user_id])} xabar/daqiqa"
    
    return False, None

def bloklangan_xabar(user_id, sabab):
    """Bloklangan xabar uchun javob"""
    return f"🚫 Xabar bloklandi!\n\n📛 Sabab: {sabab}"

# ===== TELEGRAM HANDLER UCHUN =====
def anti_spam_handler(message, bot, admin_id):
    """Anti-spam handler"""
    user_id = message.from_user.id if message.from_user else None
    ism = message.from_user.first_name if message.from_user else "Noma'lum"
    
    # Admin o'tkazib yuboriladi
    if user_id == admin_id:
        return False
    
    # Spam tekshiruvi
    blok, sabab = spam_tekshir(message)
    
    if blok:
        # Adminga xabar
        try:
            bot.send_message(
                admin_id,
                f"🚫 *SPAM BLOKLANDI*\n\n"
                f"👤 {ism}\n"
                f"🆔 {user_id}\n"
                f"📛 Sabab: {sabab}\n"
                f"💬 Xabar: {message.text[:100] if message.text else 'Media'}",
                parse_mode='Markdown'
            )
        except: pass
        
        # Foydalanuvchiga xabar
        try:
            bot.send_message(
                message.chat.id,
                f"🚫 Xabaringiz bloklandi.\n\nSabab: {sabab}\n\nIltimos, qoidalarga rioya qiling."
            )
        except: pass
        
        return True
    
    return False

print("✅ Anti-spam moduli yuklandi")