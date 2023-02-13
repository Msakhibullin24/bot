from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup

from app.states.common import CustomState, cancel_button, back_button, save_button, chosen_surname_button, \
    chosen_name_button, chosen_patronymic_button, chosen_phone_number_button

start_edit_parent_keyboard = InlineKeyboardMarkup(row_width=1)
start_edit_parent_keyboard.add(
    chosen_surname_button, chosen_name_button, chosen_patronymic_button, chosen_phone_number_button
)
start_edit_parent_keyboard.row(cancel_button, save_button)

edit_parent_keyboard = InlineKeyboardMarkup(row_width=2)
edit_parent_keyboard.row(back_button, cancel_button)


class EditParentStatesGroup(StatesGroup):
    start = CustomState(message_text='Выберите, что нужно изменить', keyboard=start_edit_parent_keyboard)
    waiting_for_surname = CustomState(message_text='Введите другую фамилию', keyboard=edit_parent_keyboard)
    waiting_for_name = CustomState(message_text='Введите другое имя', keyboard=edit_parent_keyboard)
    waiting_for_patronymic = CustomState(message_text='Введите другое отчество', keyboard=edit_parent_keyboard)
    waiting_for_phone_number = CustomState(message_text='Введите другой номер телефона', keyboard=edit_parent_keyboard)
