from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup

from app.states.common import CustomState, cancel_button, back_button, create_button

start_registration_keyboard = InlineKeyboardMarkup(row_width=1)
start_registration_keyboard.add(cancel_button)

registration_keyboard = InlineKeyboardMarkup(row_width=2)
registration_keyboard.add(back_button, cancel_button)

end_registration_keyboard = InlineKeyboardMarkup(row_width=3)
end_registration_keyboard.add(back_button, cancel_button, create_button)


class RegistrationParentStatesGroup(StatesGroup):
    waiting_for_surname = CustomState(message_text='Регистрация\nВведите фамилию', keyboard=start_registration_keyboard)
    waiting_for_name = CustomState(message_text='Введите имя', keyboard=registration_keyboard)
    waiting_for_patronymic = CustomState(message_text='Введите отчество', keyboard=registration_keyboard)
    waiting_for_phone_number = CustomState(message_text='Введите номер телефона', keyboard=registration_keyboard)
    end = CustomState(message_text='Создать?', keyboard=end_registration_keyboard)
