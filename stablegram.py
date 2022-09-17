import os, logging, random, time, sys
from uuid import uuid4
from io import BytesIO
from telegram import Bot, Update, error, InlineQueryResultCachedPhoto
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

async def photoUpload(photoMems, prompt):
    if prompt in photoLog.keys():
        return photoLog[prompt]
    else:
        photoList = []
        for i in range(2):
            photoMem = photoMems[i]
            uploadedPhoto = await bot.send_photo(chat_id=os.getenv("CHATID"), photo=photoMem, caption=prompt)
            photoList.append(uploadedPhoto)
        photoLog[prompt] = photoList
        return photoList

async def inliner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if query == "":
        return
    else:
        query = "hello jungle"
        images = apiStable.text2image(query)
        with BytesIO() as image1, BytesIO() as image2:
            photoMems = [image1, image2]
            for i in range(2):
                images[i].save(photoMems[i], format="JPEG", quality=97)
                photoMems[i].seek(0)
            
            photoList = await photoUpload([image1, image2], query)

    results = [
                InlineQueryResultCachedPhoto(
                    id=uuid4(),
                    photo_file_id= photoList[0]["photo"][-1]["file_id"]
                    ),
                InlineQueryResultCachedPhoto(
                    id=uuid4(),
                    photo_file_id= photoList[1]["photo"][-1]["file_id"]
                    )
                ]

    await update.inline_query.answer(results)


if __name__ == '__main__':
    print("Starting AUTOMATIC1111 launch checks...")
    sys.path += ['../../stablediff/stable-diffusion-webui/']
    import launch
    import apiStable

    print("Starting bot...")
    start_time = time.time()

    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

    photoLog = {}

    replier_handler = MessageHandler(filters.TEXT, replier)
    inline_handler = InlineQueryHandler(inliner)

    application.add_handler(replier_handler)
    application.add_handler(inline_handler)

    print(f"Starting polling...[{time.time() - start_time:.5f}s]")
    
    application.run_polling()
