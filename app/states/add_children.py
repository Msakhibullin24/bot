from aiogram.dispatcher.filters.state import StatesGroup

from app.states.common import CustomState
from states.registration import start_registration_keyboard, registration_keyboard, end_registration_keyboard


class AddChildrenStatesGroup(StatesGroup):
    waiting_for_surname = CustomState(message_text='Введите фамилию ребенка', keyboard=start_registration_keyboard)
    waiting_for_name = CustomState(message_text='Введите имя ребенка', keyboard=registration_keyboard)
    waiting_for_patronymic = CustomState(message_text='Введите отчество ребенка', keyboard=registration_keyboard)
    waiting_for_date_of_birth = CustomState(message_text='Введите дату рождения ребенка в формате ДД.ММ.ГГГГ',
                                            keyboard=registration_keyboard)
    end = CustomState(message_text='Создать?', keyboard=end_registration_keyboard)
