from datetime import datetime
from typing import Optional, Union

import phonenumbers
from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton

from app import config

bot = Bot(token=config.TOKEN)


class CustomState(State):
    def __init__(self, message_text: str, keyboard: Optional[InlineKeyboardMarkup] = None,
                 state: Optional[str] = None, group_name: Optional[str] = None):
        super().__init__(state, group_name)
        self.message_text = message_text
        self.keyboard = keyboard

    async def apply(self, message: types.Message = None, callback_query: types.CallbackQuery = None,
                    message_text: Optional[str] = None,
                    keyboard: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None):
        await self.set()
        if callback_query:
            await callback_query.message.edit_text(text=message_text if message_text else self.message_text)
            if keyboard:
                return await callback_query.message.edit_reply_markup(reply_markup=keyboard)
            elif self.keyboard:
                return await callback_query.message.edit_reply_markup(reply_markup=self.keyboard)
        elif message:
            return await message.answer(
                text=message_text if message_text else self.message_text,
                reply_markup=keyboard if keyboard else self.keyboard
            )


start_keyboard = InlineKeyboardMarkup()
registration_button = InlineKeyboardButton('Регистрация', callback_data='registration')
about_button = InlineKeyboardButton('About', callback_data='about')
start_keyboard.add(registration_button, about_button)


class StartStatesGroup(StatesGroup):
    start = CustomState(message_text='Start bot', keyboard=start_keyboard)


back_button = InlineKeyboardButton('Назад', callback_data='back')
cancel_button = InlineKeyboardButton('Отмена', callback_data='cancel')
create_button = InlineKeyboardButton('Создать', callback_data='create')
delete_button = InlineKeyboardButton('Удалить', callback_data='delete')
save_button = InlineKeyboardButton('Сохранить', callback_data='save')
pay_button = InlineKeyboardButton('Оплатить', callback_data='pay')

previous_button = InlineKeyboardButton('Предыдущая страница', callback_data='previous')
next_button = InlineKeyboardButton('Следующая страница', callback_data='next')

chosen_surname_button = InlineKeyboardButton('Фамилию', callback_data='chosen_surname')
chosen_name_button = InlineKeyboardButton('Имя', callback_data='chosen_name')
chosen_patronymic_button = InlineKeyboardButton('Отчество', callback_data='chosen_patronymic')
chosen_phone_number_button = InlineKeyboardButton('Номер телефона', callback_data='chosen_phone_number')
chosen_date_of_birth_button = InlineKeyboardButton('Дату рождения', callback_data='chosen_date_of_birth')


def check_phone_number_is_valid(message_text):
    try:
        phone_number = phonenumbers.parse(message_text, 'RU')
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    if not phonenumbers.is_valid_number(phone_number):
        return False
    return True


def check_date_of_birth_is_valid(message_text):
    try:
        datetime.strptime(message_text, '%d.%m.%Y')
    except ValueError:
        return False
    return True
