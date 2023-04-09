from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

audio = KeyboardButton('Audio')
video = KeyboardButton('Video')


markup_keyboard_source = ReplyKeyboardMarkup(
    resize_keyboard=True, 
    one_time_keyboard=True
    ).row(
    audio,
    video,
)

markup_yt = ReplyKeyboardMarkup(
    resize_keyboard=True, 
    
    ).add(
    KeyboardButton("Audio from YouTube video")
    ).add(
    KeyboardButton("YouTube video")
    ).add(
    KeyboardButton("YouTube Shorts")
    )