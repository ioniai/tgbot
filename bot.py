import random
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_ЗДЕСЬ")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

CHOICES = {"rock": "🪨 Камень", "scissors": "✂️ Ножницы", "paper": "📄 Бумага"}
WINS = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

def get_result(player, bot):
    if player == bot: return "draw"
    return "win" if WINS[player] == bot else "lose"

def game_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪨", callback_data="rock"),
         InlineKeyboardButton("✂️", callback_data="scissors"),
         InlineKeyboardButton("📄", callback_data="paper")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats"),
         InlineKeyboardButton("🔄 Сброс", callback_data="reset")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "stats" not in context.user_data:
        context.user_data["stats"] = {"wins": 0, "losses": 0, "draws": 0}
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n\n🪨✂️📄 Камень-ножницы-бумага!\n\nВыбери ход:",
        reply_markup=game_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "stats" not in context.user_data:
        context.user_data["stats"] = {"wins": 0, "losses": 0, "draws": 0}
    stats = context.user_data["stats"]
    action = query.data

    if action == "reset":
        context.user_data["stats"] = {"wins": 0, "losses": 0, "draws": 0}
        await query.edit_message_text("🔄 Сброшено!\n\nВыбери ход:", reply_markup=game_keyboard())
        return

    if action == "stats":
        w, l, d = stats["wins"], stats["losses"], stats["draws"]
        total = w + l + d
        wr = round(w/total*100) if total > 0 else 0
        await query.edit_message_text(
            f"📊 Статистика:\n\n🎮 Игр: {total}\n✅ Победы: {w}\n❌ Поражения: {l}\n🤝 Ничьи: {d}\n🏆 Винрейт: {wr}%",
            reply_markup=game_keyboard()
        )
        return

    if action in CHOICES:
        bot_choice = random.choice(list(CHOICES.keys()))
        result = get_result(action, bot_choice)
        if result == "win": stats["wins"] += 1
        elif result == "lose": stats["losses"] += 1
        else: stats["draws"] += 1
        w, l, d = stats["wins"], stats["losses"], stats["draws"]
        emoji = {"win": "🎉 Ты победил!", "lose": "😔 Бот победил!", "draw": "🤝 Ничья!"}
        await query.edit_message_text(
            f"Ты: {CHOICES[action]}\nБот: {CHOICES[bot_choice]}\n\n{emoji[result]}\n\n✅{w} ❌{l} 🤝{d}\n\nЕщё раз?",
            reply_markup=game_keyboard()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
