import time
import asyncio
import os
from shutil import rmtree

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger import logger
import keyboards.inline_keyboards as ik
import keyboards.keyboard_bottons as bk
from get_link import GetLink, GetResponse
from downloaders.youtube_downloader import send_video, send_audio
from templates.helper import m
from templates.greeting import g
from validator import validate_url

TOKEN = os.environ['TOKEN']

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

content_type = ''


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} {message.from_user.full_name} registred {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text=g, parse_mode="HTML")


@dp.message_handler(commands=["help"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} {message.from_user.full_name} asked help {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text=m, parse_mode="HTML")


@dp.message_handler(commands=["response"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} {message.from_user.full_name} left response {message.text} {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text=f"Left a response")
    await GetResponse.waiting_for_response.set()

    @dp.message_handler(state=GetResponse.waiting_for_response)
    async def send_response(message: types.Message, state: FSMContext, ):
        await state.finish()
        response = message.text
        logger.info(f"User {message.from_user.id}|{message.from_user.full_name} left response {response}")
        await bot.send_message(chat_id=message.chat.id, text=f"Thank you !{message.chat.id}")
        with open('bot.log', "rb") as f:
            document = types.InputFile(f)
            await bot.send_document(chat_id=404237030, document=document)


@dp.message_handler(commands=["download"])
async def cmd_botton(message: types.Message):
    logger.info(f"{message.from_user.id}|{message.from_user.full_name} choose {message.text}")
    await message.reply("*To start working press the botton*", reply_markup=bk.markup_keyboard_source,
                        parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ['YouTube', 'Instagram', 'TikTok', 'Internet'])
async def filter_sources(message: types.Message):
    usr_choise = message.text
    await message.reply(text=f'What do you want to download from *{usr_choise}*',
                        reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
    logger.info(f"{message.from_user.id}|{message.from_user.full_name} choose {usr_choise}")
    if usr_choise == "YouTube":
        await message.answer("Choose one option", reply_markup=ik.markup_yt)
    else:
        logger.error(f"Unvalid user response {usr_choise}")
        await bot.send_message(chat_id=message.chat.id, text=f"Something went wrong({usr_choise})")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('yt_'))
async def youtube_processer(callback_query: types.CallbackQuery):
    global content_type
    content_type = callback_query.data.split('_')[1]
    logger.info(f"{callback_query.from_user.id}|{callback_query.from_user.full_name} choose {content_type}")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'*Paste a link or search video using @<botname> inline mode:*', parse_mode="Markdown")
    await GetLink.waiting_for_link.set()

    @dp.message_handler(lambda message: message.from_user.id == callback_query.from_user.id,
                        state=GetLink.waiting_for_link)
    async def process_link(message: types.Message, state: FSMContext, ):
        await bot.send_message(chat_id=message.chat.id, text="Got a link, processing it")
        logger.info(f"{message.from_user.id}|{message.from_user.full_name} sent a link")
        link = message.text
        if message.text != "/exit" and validate_url(link):
            await state.finish()
            if content_type == "audio":
                try:
                    logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES BEGINS")
                    await bot.send_message(chat_id=message.chat.id, text="It may take some time.")
                    audio_name = send_audio(link)
                    with open(f'{audio_name}.mp3', 'rb') as audio:

                        await bot.send_audio(chat_id=message.chat.id, audio=audio)
                        logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES ENDS")
                except Exception as er:
                    await message.reply(f"There was an error: \n{er}")
                    logger.error(f"There was an error: {er}")
            elif content_type == "video":
                try:
                    logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES BEGINS")
                    video = send_video(link)
                    await bot.send_video(chat_id=message.chat.id, video=video)
                    logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES ENDS")
                except Exception as er:
                    await message.reply(f"There was an error: \n{er}")
                    logger.error(f"There was an error:\n {er}")
            else:
                await bot.send_message(callback_query.from_user.id,
                                       f'{callback_query.from_user.full_name} = {content_type}|FAILED ')
        elif message.text == "/exit":
            await state.finish()
            await message.reply(f"Now you can choose another option")
        else:
            logger.error(f"{message.from_user.full_name} did not sent correct link")
            await message.reply(
                f"It doesn`t seem like a correct link. Try one more time\nIf you want to change option, press /exit")


@dp.inline_handler()
async def search_videos_inline(query: InlineQuery):
    try:
        search_response = youtube.search().list(
            q=query.query,
            type='video',
            part='id,snippet',
            maxResults=10
        ).execute()

        results = []

        for search_result in search_response.get('items', []):
            video_url = f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
            title = search_result['snippet']['title']
            description = search_result['snippet']['description']
            thumbnail_url = search_result['snippet']['thumbnails']['high']['url']

            # Create a message with a video result
            message = types.InputTextMessageContent(
                message_text=video_url,
                parse_mode='HTML',
                disable_web_page_preview=True
            )

            # Add the result to the list of results
            results.append(types.InlineQueryResultArticle(
                id=search_result['id']['videoId'],
                title=title,
                description=description,
                input_message_content=message,
                thumb_url=thumbnail_url
            ))

        # Return the list of results to Telegram
        await bot.answer_inline_query(query.id, results)

    except HttpError as e:
        print(f'An error occurred: {e}')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
