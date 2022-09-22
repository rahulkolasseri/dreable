import logging
import os, sys, time
from uuid import uuid4
from io import BytesIO
from telegram import Bot, Update, InlineQueryResultCachedPhoto, InputMediaPhoto
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder, InlineQueryHandler


async def replier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat != None:
        #messageID = update.message.message_id
        fromuser = update.message.from_user.username
        messagecontent = update.message.text
        if messagecontent == "exit" and fromuser == "omgitsrahul":
            await bot.send_message(chat_id=update.effective_chat.id, text="exiting")
            # with open(r"C:\Users\rahul\Documents\Python Scripts\dreable\.env", "a") as f: 
            #     f.write(f"\nOWNER_CHAT_ID = {update.effective_chat.id}")
            sys.exit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text="hec")

async def photoCreateUpload(prompt):
    if prompt in photoLog.keys():
        #print("sameold")
        return photoLog[prompt]
    else:
        #print("new!")
        start_time = time.time()
        prompt = prompt.split("^")
        for i in range(len(prompt)):
            try:
                if i!=5:
                    prompt[i] = int(prompt[i])
                else:
                    prompt[i] = float(prompt[i])
            except ValueError:
                pass
        images, vram_info = apiStable.text2image(*prompt)

        imageCreationTime = time.time() - start_time
        print(f"image creation took {imageCreationTime:.5f} seconds")
        print(vram_info)

        start_time = time.time()
        photoMems = []
        for i in range(len(images)):
            with BytesIO() as tempfile:
                images[i].save(tempfile, format="JPEG", quality=90, optimize=True, progressive=True)
                size = tempfile.tell()
                tempfile.seek(0)
                photoMems.append(InputMediaPhoto(media=tempfile, caption=prompt[0] + f" {size/1000:.3f} KB {imageCreationTime:.3f}s"))
        print(f"image saving took {time.time() - start_time:.5f} seconds")

        # with BytesIO() as image1: , BytesIO() as image2:
        #     photoMems.append(image1)
        #         images[i].save(photoMems[i], format="JPEG", quality=97)
        #         photoMems[i].seek(0)
        #         photoMems[i] = InputMediaPhoto(photoMems[i])
        
        start_time = time.time()        
        uploadedPhotoSet = await bot.sendMediaGroup(chat_id=os.getenv("CHAT_ID"), media=photoMems)
        print(f"image uploading took {time.time() - start_time:.5f} seconds")
        photoLog["^".join(str(prompt))] = uploadedPhotoSet
        return uploadedPhotoSet

async def inliner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_time = time.time()
    query = update.inline_query.query

    if query == "":
        return
    if query[-1] != ".":
        return
    else:
        query = query[:-1]
        photoList = await photoCreateUpload(query)
        #print(photoList)
    
    results = []
    for i in range(len(photoList)):
        results.append(InlineQueryResultCachedPhoto(
            id=uuid4(),
            photo_file_id=photoList[i].photo[-1].file_id
        ))

    # results = [
    #             InlineQueryResultCachedPhoto(
    #                 id=uuid4(),
    #                 photo_file_id= photoList[0]["photo"][-1]["file_id"]
    #                 ),
    #             InlineQueryResultCachedPhoto(
    #                 id=uuid4(),
    #                 photo_file_id= photoList[1]["photo"][-1]["file_id"]
    #                 )
    #             ]
    print("query: " + query + f" answered in {time.time() - start_time:.5f} seconds")
    await update.inline_query.answer(results)

async def closePlease(application: ApplicationBuilder):
    os._exit(0)

async def startup(application: ApplicationBuilder, start_time=time.time()):
    now = time.time()
    if start_time - now < 1:
        timeMsg = ""
    else:
        timeMsg = f" in {now - start_time:.2f} seconds"
    await bot.sendMessage(chat_id=os.getenv("OWNER_CHAT_ID"), text= f"Bot started{timeMsg}" )


if __name__ == "__main__":
    cwd = os.getcwd()
    logging.basicConfig(
    filename = "debuglog.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)


    application = ApplicationBuilder()
    application.token(os.getenv("TELEGRAM_TOKEN"))
    application.post_shutdown(closePlease)
    application = application.build()
    
    print("Loading up Stable Diffusion")
    start_time = time.time()
    os.chdir(cwd+"/A1111NoUI/")
    sys.path += [cwd+'/A1111NoUI']
    print(os.getcwd())
    import apiStable

    print("Running first query to warm up the model")

    apiStable.text2image("Hello world", w=320, h=320, batch_size=4, steps=15, cfg=7.0, seed=-1, sampler=0)

    print("Starting bot...")
    
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

    photoLog = {}

    replier_handler = MessageHandler(filters.TEXT, replier)
    inline_handler = InlineQueryHandler(inliner)

    application.add_handler(replier_handler)
    application.add_handler(inline_handler)

    print(f"Starting polling...[{time.time() - start_time:.5f}s]")

    
    
    application.run_polling()