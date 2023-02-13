from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.states.common import CustomState


parent_keyboard = InlineKeyboardMarkup(row_width=1)
parent_update_button = InlineKeyboardButton('Редактировать профиль', callback_data='edit_parent')
add_children_button = InlineKeyboardButton('Добавить ребенка', callback_data='add_children')
children_list_button = InlineKeyboardButton('Мои дети', callback_data='children_list')
parent_keyboard.add(parent_update_button, add_children_button, children_list_button)


class ParentStatesGroup(StatesGroup):
    start = CustomState(message_text='Главное меню родителя', keyboard=parent_keyboard)
