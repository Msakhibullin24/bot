from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.states.common import CustomState, delete_button, back_button, cancel_button, pay_button

action_keyboard = InlineKeyboardMarkup()
# action_keyboard.row(pay_button)
action_keyboard.add(delete_button)
action_keyboard.row(back_button, cancel_button)


class RequestListStatesGroup(StatesGroup):
    waiting_for_request = CustomState(message_text='Заявки')
    waiting_for_action = CustomState(message_text='Выберите действие', keyboard=action_keyboard)
    end = CustomState(message_text='Точно', keyboard=action_keyboard)
