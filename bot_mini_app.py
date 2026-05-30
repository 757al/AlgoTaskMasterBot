import os
import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from database import (
    init_db, add_task, get_tasks, complete_task, delete_task,
    get_user_stats, get_all_users, delete_user_by_id
)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
app = ApplicationBuilder().token(TOKEN).build()
init_db()

print(f"DEBUG: TOKEN = {TOKEN[:10] if TOKEN else 'None'}...")

ADMIN_ID = 1657525561  # замени на свой Telegram ID

def is_admin(user_id):
    return user_id == ADMIN_ID

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["📋 Мои задачи", "➕ Добавить задачу"],
        ["✅ Выполнить", "❌ Удалить"],
        ["👑 Админ панель", "❓ Помощь"]
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["📊 Статистика", "👥 Пользователи"],
        ["🗑 Удалить пользователя", "◀️ Главное меню"]
    ], resize_keyboard=True)

# ========== ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ ==========
async def start(update, context):
    await update.message.reply_text(
        "📌 *Менеджер задач*\n\n"
        "➕ `/add Задача` — добавить\n"
        "📋 `/list` — список\n"
        "✅ `/done 1` — выполнить\n"
        "❌ `/delete 1` — удалить\n\n"
        "Кнопки тоже работают.",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_command(update, context):
    await update.message.reply_text(
        "📖 *Помощь*\n\n"
        "/add текст — добавить\n"
        "/list — показать задачи\n"
        "/done номер — выполнить\n"
        "/delete номер — удалить",
        parse_mode="Markdown"
    )

async def add(update, context):
    try:
        task = ' '.join(context.args)
        if not task:
            await update.message.reply_text("❌ Пример: `/add Сделать уроки`", parse_mode="Markdown")
            return
        add_task(update.effective_user.id, task)
        await update.message.reply_text(f"✅ Задача добавлена: *{task}*", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Ошибка при добавлении")

async def list_tasks(update, context):
    tasks = get_tasks(update.effective_user.id)
    if not tasks:
        await update.message.reply_text("📭 Нет активных задач")
        return
    msg = "📋 *Список задач:*\n"
    for tid, text in tasks:
        msg += f"\n🔹 `{tid}`. {text}"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def done(update, context):
    try:
        tid = int(context.args[0])
        complete_task(tid, update.effective_user.id)
        await update.message.reply_text(f"✅ Задача {tid} выполнена")
    except:
        await update.message.reply_text("❌ `/done 1`", parse_mode="Markdown")

async def delete(update, context):
    try:
        tid = int(context.args[0])
        delete_task(tid, update.effective_user.id)
        await update.message.reply_text(f"🗑 Задача {tid} удалена")
    except:
        await update.message.reply_text("❌ `/delete 1`", parse_mode="Markdown")

# ========== АДМИН-КОМАНДЫ ==========
async def admin_panel(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Нет доступа")
        return
    await update.message.reply_text("👑 *Админ-панель*", parse_mode="Markdown", reply_markup=admin_keyboard())

async def admin_stats(update, context):
    if not is_admin(update.effective_user.id):
        return
    total_users, total_tasks, active, done = get_user_stats()
    await update.message.reply_text(
        f"📊 *Статистика*\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"📝 Всего задач: {total_tasks}\n"
        f"✅ Активных: {active}\n"
        f"✔ Выполнено: {done}",
        parse_mode="Markdown"
    )

async def admin_users(update, context):
    if not is_admin(update.effective_user.id):
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("Нет пользователей")
        return
    msg = "👥 *Список пользователей:*\n\n"
    for uid, name, username, joined in users:
        msg += f"🆔 {uid} — {name} (@{username})\n📅 {joined[:10]}\n\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def admin_deluser(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        uid = int(context.args[0])
        if uid == ADMIN_ID:
            await update.message.reply_text("❌ Нельзя удалить себя")
            return
        delete_user_by_id(uid)
        await update.message.reply_text(f"✅ Пользователь {uid} удалён")
    except:
        await update.message.reply_text("❌ `/deluser 123456789`", parse_mode="Markdown")

# ========== ОБРАБОТЧИК КНОПОК ==========
async def handle_buttons(update, context):
    text = update.message.text
    if text == "📋 Мои задачи":
        await list_tasks(update, context)
    elif text == "➕ Добавить задачу":
        await update.message.reply_text("✏️ `/add Купить хлеб`", parse_mode="Markdown")
    elif text == "✅ Выполнить":
        await update.message.reply_text("✏️ `/done 1`", parse_mode="Markdown")
    elif text == "❌ Удалить":
        await update.message.reply_text("✏️ `/delete 1`", parse_mode="Markdown")
    elif text == "👑 Админ панель":
        await admin_panel(update, context)
    elif text == "📊 Статистика":
        await admin_stats(update, context)
    elif text == "👥 Пользователи":
        await admin_users(update, context)
    elif text == "🗑 Удалить пользователя":
        await update.message.reply_text("✏️ `/deluser 123456789`", parse_mode="Markdown")
    elif text == "◀️ Главное меню":
        await start(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)

# ========== ЗАПУСК ==========
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("admin_panel", admin_panel))
app.add_handler(CommandHandler("stats", admin_stats))
app.add_handler(CommandHandler("users", admin_users))
app.add_handler(CommandHandler("deluser", admin_deluser))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

if __name__ == "__main__":
    print("✅ Бот запущен (учебная версия с админкой)")
    app.run_polling()
