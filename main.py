import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

# --- SOZLAMALAR ---
BOT_TOKEN = "9291368937:AAHUn5SK_Or3HsV_G3aMQFTWJVzklvbDiW8"
ADMIN_ID = 8512219786

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

users_db = {}  
games = {}     

SUPPORTED_LANGUAGES = {
    "uz": "O'zbekcha 🇺🇿",
    "ru": "Русский 🇷🇺",
    "en": "English 🇬🇧",
    "az": "Azərbaycan 🇦🇿",
    "tr": "Türkçe 🇹🇷",
    "kz": "Қазақша 🇰🇿",
    "fa": "فارسی 🇮🇷"
}

translations = {
    "uz": {
        "welcome": "🎭 **Mafia Baku 2** botiga xush kelibsiz!",
        "lang_set": "✅ Til O'zbek tiliga o'zgartirildi.",
        "balance": "Sizning almazlaringiz",
        "buy_btn": "💎 Almaz sotib olish",
        "admin_welcome": "👑 Admin panelga xush kelibsiz!"
    },
    "ru": {
        "welcome": "🎭 Добро пожаловать в бота **Mafia Baku 2**!",
        "lang_set": "✅ Язык изменен на Русский.",
        "balance": "Ваши алмазы",
        "buy_btn": "💎 Купить алмазы",
        "admin_welcome": "👑 Добро пожаловать в админ-панель!"
    },
    "en": {
        "welcome": "🎭 Welcome to **Mafia Baku 2** bot!",
        "lang_set": "✅ Language changed to English.",
        "balance": "Your diamonds",
        "buy_btn": "💎 Buy Diamonds",
        "admin_welcome": "👑 Welcome to Admin Panel!"
    },
    "az": {
        "welcome": "🎭 **Mafia Baku 2** botuna xoş gəlmisiniz!",
        "lang_set": "✅ Dil Azərbaycan dilinə dəyişdirildi.",
        "balance": "Almazlarınız",
        "buy_btn": "💎 Almaz al",
        "admin_welcome": "👑 Admin panelinə xoş gəlmisiniz!"
    },
    "tr": {
        "welcome": "🎭 **Mafia Baku 2** botuna hoş geldiniz!",
        "lang_set": "✅ Dil Türkçe olarak değiştirildi.",
        "balance": "Elmaslarınız",
        "buy_btn": "💎 Elmas Satın Al",
        "admin_welcome": "👑 Admin Paneline Hoş Geldiniz!"
    },
    "kz": {
        "welcome": "🎭 **Mafia Baku 2** ботына қош келдіңіз!",
        "lang_set": "✅ Тіл Қазақ тіліне өзгертілді.",
        "balance": "Алmasтарыңыз",
        "buy_btn": "💎 Алмас сатып алу",
        "admin_welcome": "👑 Әкімші панеліне қош келдіңіз!"
    },
    "fa": {
        "welcome": "🎭 به ربات **Mafia Baku 2** خوش آمدید!",
        "lang_set": "✅ زبان به فارسی تغییر یافت.",
        "balance": "الماس‌های شما",
        "buy_btn": "💎 خرید الماس",
        "admin_welcome": "👑 به پنل مدیریت خوش آمدید!"
    }
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 50, "lang": "uz", "name": message.from_user.full_name}

    lang = users_db[user_id]["lang"]
    text = translations.get(lang, translations["uz"])["welcome"]

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🎮 O'yinni boshlash (Guruhda)", callback_data="info_group")],
            [types.InlineKeyboardButton(text="🌐 Tilni o'zgartirish / Language", callback_data="change_lang")],
            [types.InlineKeyboardButton(text="💎 Almaz Balansi", callback_data="balance")]
        ]
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "change_lang")
async def choose_language(callback: types.CallbackQuery):
    keyboard_buttons = []
    for code, name in SUPPORTED_LANGUAGES.items():
        keyboard_buttons.append([types.InlineKeyboardButton(text=name, callback_data=f"set_lang_{code}")])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text("Tilni tanlang / Choose your language:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[2]
    user_id = callback.from_user.id
    
    if user_id in users_db:
        users_db[user_id]["lang"] = lang_code
    
    text = translations.get(lang_code, translations["uz"])["lang_set"]
    await callback.answer(text, show_alert=True)
    await cmd_start(callback.message)

@dp.callback_query(F.data == "balance")
async def show_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = users_db.get(user_id, {"balance": 0, "lang": "uz"})
    lang = user_data["lang"]
    balance = user_data["balance"]
    
    trans = translations.get(lang, translations["uz"])
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=trans["buy_btn"], callback_data="buy_almaz")],
            [types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_start")]
        ]
    )
    await callback.message.edit_text(f"💎 {trans['balance']}: **{balance} 💎**", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "buy_almaz")
async def buy_almaz(callback: types.CallbackQuery):
    await callback.message.answer(
        "💎 **Almaz sotib olish va to'lov usullari:**\n\n"
        "• Click / Payme / Uzcard\n"
        "• USDT / Kriptovalyuta\n\n"
        "Murojaat uchun bot adminiga yozing: @Admin",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_start")
async def back_start(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_start(callback.message)

@dp.callback_query(F.data == "info_group")
async def info_group(callback: types.CallbackQuery):
    await callback.answer("Mafiya o'yinini boshlash uchun meni istalgan guruhga qo'shib /mafia deb yozing!", show_alert=True)

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda bu buyruqni ishlatish uchun huquq yo'q! ❌")
        return

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="💎 Almaz Tarqatish (/give)", callback_data="admin_help_give")],
            [types.InlineKeyboardButton(text="📊 Bot Statistikasi", callback_data="admin_stats")]
        ]
    )
    await message.answer("👑 **Admin Panelga xush kelibsiz!**", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    total_users = len(users_db)
    total_games = len(games)
    await callback.message.answer(
        f"📊 **Bot Statistikasi:**\n\n"
        f"👥 Foydalanuvchilar soni: {total_users} ta\n"
        f"🎮 Faol o'yinlar soni: {total_games} ta",
        parse_mode="Markdown"
    )

@dp.message(Command("give"))
async def give_almaz(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Xato format! Ishlatilishi: `/give <user_id> <miqdor>`", parse_mode="Markdown")
        return
    
    target_id = int(args[1])
    amount = int(args[2])
    
    if target_id in users_db:
        users_db[target_id]["balance"] += amount
        await message.answer(f"✅ Muvaffaqiyatli! ID: {target_id} ga {amount} 💎 almaz qo'shildi.")
        try:
            await bot.send_message(target_id, f"🎁 Sizga admin tomonidan {amount} 💎 almaz taqdim etildi!")
        except:
            pass
    else:
        await message.answer("⚠️ Foydalanuvchi bazada topilmadi (u avval botga /start bosmagan).")

@dp.message(Command("mafia", "start_mafia"))
async def start_mafia_game(message: types.Message):
    if message.chat.type == "private":
        await message.answer("Bu buyruq faqat mafiya guruhlarida ishlaydi! ❌")
        return

    chat_id = message.chat.id
    
    if chat_id in games and games[chat_id]["status"] == "active":
        await message.answer("Bu guruhda o'yin allaqachon boshlangan! ⚠️")
        return

    games[chat_id] = {
        "players": [],
        "status": "waiting"
    }

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🎮 O'yinga qo'shilish", callback_data="join_game")],
            [types.InlineKeyboardButton(text="🚀 O'yinni boshlash", callback_data="start_playing")]
        ]
    )

    await message.answer(
        "🎭 **Mafia Baku 2 — O'yin boshlanmoqda!**\n\n"
        "Ishtirok etish uchun pastdagi tugmani bosing:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "join_game")
async def join_game(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in games or games[chat_id]["status"] != "waiting":
        await callback.answer("Hozir o'yinga qo'shilib bo'lmaydi.", show_alert=True)
        return

    players = games[chat_id]["players"]
    
    if user.id in [p["id"] for p in players]:
        await callback.answer("Siz allaqachon ro'yxatdasiz! ✅", show_alert=True)
        return

    players.append({"id": user.id, "name": user.full_name})
    await callback.answer("Siz o'yinga muvaffaqiyatli qo'shildingiz! 🎉")

    player_list = "\n".join([f"• {p['name']}" for p in players])
    try:
        await callback.message.edit_text(
            f"🎭 **Mafia Baku 2 — O'yin boshlanmoqda!**\n\n"
            f"Ishtirokchilar ({len(players)} ta):\n{player_list}\n\n"
            f"O'yin boshlanishi uchun kamida 4 kishi kerak.",
            reply_markup=callback.message.reply_markup,
            parse_mode="Markdown"
        )
    except Exception:
        pass

@dp.callback_query(F.data == "start_playing")
async def start_playing(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in games or games[chat_id]["status"] != "waiting":
        return

    players = games[games_chat_id := chat_id]["players"]

    if len(players) < 4:
        await callback.answer("O'yin boshlash uchun kamida 4 kishi kerak! ⚠️", show_alert=True)
        return

    games[chat_id]["status"] = "active"

    roles = ["Mafiya 🦹‍♂️", "Doktor 💉", "Komissar 🕵️‍♂️"]
    while len(roles) < len(players):
        roles.append("Tinch aholi 👨‍🌾")

    random.shuffle(roles)
    
    for i, player in enumerate(players):
        player["role"] = roles[i]
        try:
            await bot.send_message(
                player["id"],
                f"🎲 Sizning mafiya o'yinidagi rolingiz: **{roles[i]}**\n"
                f"Sizga omad tilaymiz!",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.message.edit_text(
        f"🚀 **O'yin boshlandi!**\n\n"
        f"Isht

