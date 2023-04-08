from aiogram.dispatcher.filters.state import State, StatesGroup


# Define states
class GetLink(StatesGroup):
    waiting_for_link = State()

class GetResponse(StatesGroup):
    waiting_for_response = State()






