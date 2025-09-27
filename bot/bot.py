from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ВАШИ ДАННЫЕ
BOT_TOKEN = "8133300846:AAFGk1qpvJR0OglStD6J4LbW3BIDU6EZGJU"
ADMIN_IDS = [6359121076]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎮 Открыть Banana Casino", web_app={"url": "https://your-domain.vercel.app"})],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance"),
         InlineKeyboardButton("📤 Перевод", callback_data="transfer")],
        [InlineKeyboardButton("⚙️ Админка", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🍌 Привет, {user.first_name}!\n\n"
        "Добро пожаловать в Banana Casino!\n\n"
        "🎰 Игры с банановой валютой\n"
        "📤 Переводы между игроками\n"
        "⚙️ Админ панель для владельца\n\n"
        "Команды:\n"
        "/start - Главное меню\n"
        "/balance - Ваш баланс\n"
        "/transfer ID СУММА - Перевод\n"
        "/admin - Админ панель",
        reply_markup=reply_markup
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"💰 Ваш ID: {user_id}\n"
        "Баланс можно посмотреть в Mini App\n\n"
        "Откройте казино для просмотра баланса!"
    )

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📤 Перевод бананов\n\n"
            "Использование:\n"
            "/transfer ID_получателя СУММА\n\n"
            "Пример:\n"
            "/transfer 123456789 100\n\n"
            "Комиссия: 5%"
        )
        return
    
    try:
        to_user_id = int(context.args[0])
        amount = int(context.args[1])
        
        await update.message.reply_text(
            f"📤 Запрос перевода:\n"
            f"Кому: {to_user_id}\n"
            f"Сумма: {amount}🍌\n"
            f"Комиссия: {amount * 0.05}🍌\n\n"
            f"Для выполнения перевода откройте Mini App!"
        )
        
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Используйте: /transfer ID СУММА")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ только для администратора")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 Выдать бананы", callback_data="admin_add")],
        [InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ Админ панель Banana Casino\n\n"
        "Доступные действия:\n"
        "• Просмотр статистики\n"
        "• Выдача бананов\n"
        "• Управление пользователями\n\n"
        "Используйте кнопки ниже:",
        reply_markup=reply_markup
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("transfer", transfer))
    application.add_handler(CommandHandler("admin", admin))
    
    print("🤖 Бот запускается...")
    application.run_polling()

if __name__ == "__main__":
    main()s

