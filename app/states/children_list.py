from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.states.common import CustomState, cancel_button, back_button

children_actions_keyboard = InlineKeyboardMarkup(row_width=1)
edit_children_button = InlineKeyboardButton('Редактировать', callback_data='edit_children')
children_request_list_button = InlineKeyboardButton('Показать список запросов', callback_data='children_request_list')
course_list_button = InlineKeyboardButton('Записать на курс', callback_data='course_list')
children_actions_keyboard.add(edit_children_button, children_request_list_button, course_list_button)
children_actions_keyboard.row(back_button, cancel_button)


class ChildrenListStatesGroup(StatesGroup):
    waiting_for_children = CustomState(message_text='Список детей')
    waiting_for_action = CustomState(message_text='Выберите действие', keyboard=children_actions_keyboard)
