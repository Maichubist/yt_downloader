from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

markup_yt = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='SOMETHING')
markup_yt.add(
    InlineKeyboardButton("Audio", callback_data="yt_audio", 
                         style='primary',    # set button style to primary
                         text_color='white', # set text color to white
                         background_color='#ff0000'), # set background color to red
    InlineKeyboardButton("Video", callback_data="yt_video", 
                         style='secondary',  # set button style to secondary
                         text_color='#00ff00', # set text color to green
                         background_color='#000000'), # set background color to black
)
markup_inst = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='SOMETHING')
markup_inst.add(
    InlineKeyboardButton("First 12 posts of profile", callback_data="inst_profile", 
                         style='primary',    # set button style to primary
                         text_color='white', # set text color to white
                         background_color='#ff0000'), # set background color to red
    InlineKeyboardButton("Video", callback_data="inst_videoi", 
                         style='secondary',  # set button style to secondary
                         text_color='#00ff00', # set text color to green
                         background_color='#000000'), # set background color to black
)
markup_tk = InlineKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='SOMETHING')
markup_tk.add(
    InlineKeyboardButton("Video", callback_data="tk_video", 
                         style='primary',    # set button style to primary
                         text_color='white', # set text color to white
                         background_color='#ff0000'), # set background color to red
)

# markup_it = markup_tk = InlineKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='SOMETHING')
# markup_it.add(
#     InlineKeyboardButton("Audio", callback_data="it_audio", 
#                          style='primary',    # set button style to primary
#                          text_color='white', # set text color to white
#                          background_color='#ff0000'), # set background color to red
#     InlineKeyboardButton("Video", callback_data="it_video", 
#                          style='secondary',  # set button style to secondary
#                          text_color='#00ff00', # set text color to green
#                          background_color='#000000'), # set background color to black
#     InlineKeyboardButton("File", callback_data="it_file", 
#                          style='link',  # set button style to link
#                          text_color='#0000ff', # set text color to blue
#                          background_color='#ffffff') # set background color to white
# )