import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Gemini Setup ─────────────────────────────────────────────────────────────
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Tu "UX DEMON AI" hai — ek powerful AI assistant jo Telegram par kaam karta hai.
Tujhe UX DEMON OFC ne banaya hai.

Teri personality:
- Naam: UX DEMON AI
- Smart, direct aur helpful
- Hinglish mein baat karta hai by default (Hindi + English mix)
- Agar user English mein bole to English mein reply kar
- Agar user Hindi mein bole to Hinglish mein reply kar
- Concise aur clear — overexplain mat kar
- Friendly tone, professional jab zaroorat ho

Tu kya kar sakta hai:
- Code likhna & debug karna (Python, JS, PHP, Java, C++ sab)
- Content writing — captions, posts, emails, essays
- Math, physics, chemistry solve karna
- Translation (koi bhi language)
- Summarization
- Creative writing — stories, poems, scripts
- Business ideas & planning
- General knowledge — koi bhi sawaal
- Aur jo bhi manga jaye!

Group chat:
- Group mein sirf tab reply kar jab @mention ho ya bot ki message pe reply ho
- Group mein short replies do

Important:
- Apna naam puchha jaye to "UX DEMON AI" bol
- Creator puchha jaye to "UX DEMON OFC" bol
- "Gemini" ya "Google" ka naam mat le — tu UX DEMON AI hai"""

# ─── Per-chat history store ───────────────────────────────────────────────────
chat_sessions = {}

def get_session(chat_id: int):
    if chat_id not in chat_sessions:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        chat_sessions[chat_id] = model.start_chat(history=[])
    return chat_sessions[chat_id]

async def ask_ai(chat_id: int, message: str) -> str:
    try:
        session = get_session(chat_id)
        response = session.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise

# ─── Helpers ──────────────────────────────────────────────────────────────────
BOT_USERNAME = "UXDEMON_AI_BOT"

def is_addressed(update: Update) -> bool:
    msg = update.message
    if not msg or not msg.text:
        return False
    if update.effective_chat.type == "private":
        return True
    text = msg.text.lower()
    if f"@{BOT_USERNAME.lower()}" in text:
        return True
    if msg.reply_to_message and msg.reply_to_message.from_user:
        if msg.reply_to_message.from_user.is_bot:
            return True
    return False

def clean_text(text: str) -> str:
    return text.replace(f"@{BOT_USERNAME}", "").replace(f"@{BOT_USERNAME.lower()}", "").strip()

def split_message(text: str, limit: int = 4000):
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts

async def send_reply(update: Update, text: str, quote: bool = False):
    parts = split_message(text)
    reply_id = update.message.message_id if quote else None
    for part in parts:
        try:
            await update.message.reply_text(
                part,
                parse_mode="Markdown",
                reply_to_message_id=reply_id,
            )
        except Exception:
            await update.message.reply_text(part, reply_to_message_id=reply_id)
        reply_id = None  # sirf pehle message mein quote

# ─── Command Handlers ─────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "bhai"
    is_group = update.effective_chat.type != "private"

    if is_group:
        text = (
            "🔥 *UX DEMON AI — Online!*\n\n"
            "Koi bhi kaam ho, bas mujhe mention karo:\n"
            f"👉 @{BOT_USERNAME} [apna message]\n\n"
            "Ya meri kisi message ko Reply karo.\n\n"
            "_Powered by UX DEMON OFC_ ⚡"
        )
    else:
        text = (
            f"🔥 *Welcome to UX DEMON AI!*\n\n"
            f"Hey {name}! Main tera AI assistant hoon.\n\n"
            "*Main kya kar sakta hoon:*\n"
            "🧠 Code likhna & debug karna\n"
            "✍️ Content & writing\n"
            "📐 Math & science\n"
            "🌍 Translation\n"
            "💡 Ideas & planning\n"
            "🎭 Creative writing\n"
            "...aur jo bhi poochho!\n\n"
            "💬 Seedha message karo — shuru karte hain!\n\n"
            "_Powered by UX DEMON OFC_ ⚡"
        )
    await send_reply(update, text)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *UX DEMON AI — Help*\n\n"
        "*Private Chat:*\n"
        "Seedha message karo, main jawab dunga.\n\n"
        "*Group Chat:*\n"
        f"• @{BOT_USERNAME} [message] — mention karo\n"
        "• Meri message ko Reply karo\n\n"
        "*Commands:*\n"
        "/start — Bot se hi karo\n"
        "/help — Yeh message\n"
        "/clear — Chat history reset\n"
        "/about — Bot ke baare mein\n\n"
        "*Example messages:*\n"
        '_"Python mein login system bana de"_\n'
        '_"Yeh paragraph English mein translate kar"_\n'
        '_"Instagram caption likh de"_\n'
        '_"5 business ideas do"_\n\n'
        "_UX DEMON OFC ⚡_"
    )
    await send_reply(update, text)

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚡ *UX DEMON AI*\n\n"
        "Main ek advanced AI assistant hoon jo har kaam kar sakta hoon.\n\n"
        "*Creator:* UX DEMON OFC\n"
        "*Platform:* Telegram\n"
        "*Capabilities:* Coding, Writing, Math, Translation, aur bahut kuch\n\n"
        '_"Koi bhi kaam ho — main karunga"_ 🔥'
    )
    await send_reply(update, text)

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in chat_sessions:
        del chat_sessions[chat_id]
    is_group = update.effective_chat.type != "private"
    msg = "🗑️ Group chat history clear!" if is_group else "🗑️ Chat history clear! Fresh start karo."
    await update.message.reply_text(msg, reply_to_message_id=update.message.message_id)

# ─── Main Message Handler ──────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not is_addressed(update):
        return

    is_group = update.effective_chat.type != "private"
    chat_id = update.effective_chat.id

    msg = update.message.text
    if is_group:
        msg = clean_text(msg)

    if not msg:
        await update.message.reply_text(
            "Haan bolo? 😊",
            reply_to_message_id=update.message.message_id
        )
        return

    # Typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        reply = await ask_ai(chat_id, msg)
        await send_reply(update, reply, quote=is_group)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "❌ Error aa gaya. Dobara try karo!",
            reply_to_message_id=update.message.message_id
        )

# ─── Media Handlers ───────────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_addressed(update) and update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "📸 Image analysis abhi available nahi. Text mein describe karo!",
        reply_to_message_id=update.message.message_id
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_addressed(update) and update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "🎙️ Voice messages nahi samajh sakta. Text type karo!",
        reply_to_message_id=update.message.message_id
    )

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text("😄 Nice sticker! Kuch kaam ho toh batao.")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN .env mein nahi hai!")
        return
    if not gemini_key:
        logger.error("GEMINI_API_KEY .env mein nahi hai!")
        return

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("clear", cmd_clear))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))

    print("✅ UX DEMON AI — Online!")
    print(f"📌 t.me/{BOT_USERNAME}")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
