import time
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger import logger
import keyboards.keyboard_bottons as kb
from get_link import GetResponse
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

user_data = {}


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
    await message.reply("Paste a link to download or use @s_yt_bot inline mode to find video in YouTube")


@dp.message_handler(lambda message: validate_url(message.text))
async def link_processor(message: types.Message):
    user_data[message.from_user.id] = {"link": message.text}
    await message.answer("Choose one option", reply_markup=kb.markup_keyboard_source)


@dp.message_handler(lambda message: message.text in ["Audio", "Video"])
async def link_processor(message: types.Message):
    global user_data
    content = message.text
    logger.info(
        f"{message.from_user.id}|{message.from_user.full_name} choose {content}")
    if content == "Audio":
        try:
            logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES BEGINS")
            await bot.send_message(chat_id=message.from_user.id, text="It may take some time.")
            audio_name = send_audio(user_data[message.from_user.id]["link"])
            with open(f'{audio_name}.mp3', 'rb') as audio:

                await bot.send_audio(chat_id=message.from_user.id, audio=audio)
                logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES ENDS")
                os.remove(f"{audio_name}.mp3")
        except Exception as er:
            await message.reply(f"There was an error: \n{er}")
            logger.error(f"There was an error: {er}")
    elif content == "Video":
        try:
            logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES BEGINS")
            video = send_video(user_data[message.from_user.id]["link"])
            await bot.send_video(chat_id=message.from_user.id, video=video)
            logger.info(f"{message.from_user.id}|{message.from_user.full_name}| THE PROCES ENDS")
        except Exception as er:
            await message.from_user.id.reply(f"There was an error: \n{er}")
            logger.error(f"There was an error:\n {er}")
    else:
        await bot.send_message(message.from_user.id,
                               f'{message.from_user.full_name} = {user_data}|FAILED ')
    logger.info(f"User {user_data} deleted")
    del user_data


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
