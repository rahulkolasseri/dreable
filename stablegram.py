import os, logging, random, time
from uuid import uuid4
from telegram import Bot, Update, error, InlineQueryResultPhoto
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder, InlineQueryHandler

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    filename = "errlog.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

async def replier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat != None:
        #messageID = update.message.message_id
        #fromuser = update.message.from_user.username
        #messagecontent = update.message.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text="hec")

async def inliner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if query == "":
        return
    
    results = [
                InlineQueryResultPhoto(
                    id=uuid4(),
                    title="URLPhoto",
                    photo_url="https://upload.wikimedia.org/wikipedia/commons/d/d8/Macintosh_classic.jpg",
                    thumb_url="https://upload.wikimedia.org/wikipedia/commons/d/d8/Macintosh_classic.jpg"
                    ),
                InlineQueryResultPhoto(
                    id=uuid4(),
                    title="URLPhoto",
                    photo_url="https://upload.wikimedia.org/wikipedia/commons/d/d8/Macintosh_classic.jpg",
                    thumb_url="https://upload.wikimedia.org/wikipedia/commons/d/d8/Macintosh_classic.jpg"
                    )
                ]

    await update.inline_query.answer(results)


if __name__ == '__main__':
    print("Starting bot...")
    start_time = time.time()

    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    replier_handler = MessageHandler(filters.TEXT, replier)
    inline_handler = InlineQueryHandler(inliner)

    application.add_handler(replier_handler)
    application.add_handler(inline_handler)

    print(f"Starting polling...[{time.time() - start_time:.5f}s]")
    
    application.run_polling()
