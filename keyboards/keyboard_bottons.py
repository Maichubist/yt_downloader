from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.utils.emoji import emojize

youtube_k = KeyboardButton('YouTube')
tiktok_k = KeyboardButton('TikTok (DON`T USE)')
instagram_k = KeyboardButton('Instagram')
internet_k = KeyboardButton('Internet (DON`T USE)')


markup_keyboard_source = ReplyKeyboardMarkup(
    resize_keyboard=True, 
    one_time_keyboard=True
    ).row(
        youtube_k)
    #     ).add(
    # internet_k
    # )

markup_yt = ReplyKeyboardMarkup(
    resize_keyboard=True, 
    
    ).add(
    KeyboardButton("Audio from YouTube video")
    ).add(
    KeyboardButton("YouTube video")
    ).add(
    KeyboardButton("YouTube Shorts")
    )