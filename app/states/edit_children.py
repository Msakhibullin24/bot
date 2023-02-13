from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup

from app.states.common import CustomState, cancel_button, back_button, delete_button

edit_children_keyboard = InlineKeyboardMarkup()
edit_children_keyboard.row(back_button, cancel_button)

delete_children_keyboard = InlineKeyboardMarkup()
delete_children_keyboard.row(back_button, cancel_button, delete_button)


class EditChildrenStatesGroup(StatesGroup):
    start = CustomState(message_text='Выберите, что нужно изменить')
    waiting_for_surname = CustomState(message_text='Введите другую фамилию', keyboard=edit_children_keyboard)
    waiting_for_name = CustomState(message_text='Введите другое имя', keyboard=edit_children_keyboard)
    waiting_for_patronymic = CustomState(message_text='Введите другое отчество', keyboard=edit_children_keyboard)
    waiting_for_date_of_birth = CustomState(message_text='Введите другую дату рождения', keyboard=edit_children_keyboard)
    waiting_for_delete = CustomState(message_text='Вы уверены?', keyboard=delete_children_keyboard)
