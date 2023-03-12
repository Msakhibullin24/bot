from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import InlineKeyboardMarkup

from app.states.common import CustomState, back_button, cancel_button, pay_button

action_keyboard = InlineKeyboardMarkup()
action_keyboard.row(pay_button)
# action_keyboard.add(delete_button)
action_keyboard.row(back_button, cancel_button)


pay_keyboard = InlineKeyboardMarkup()
pay_keyboard.row(back_button, cancel_button)


class RequestListStatesGroup(StatesGroup):
    waiting_for_request = CustomState(message_text='Заявки')
    waiting_for_action = CustomState(message_text='Выберите действие', keyboard=action_keyboard)
    delete = CustomState(message_text='Точно', keyboard=action_keyboard)
    pay = CustomState(message_text='''Добрый день! Пришлите, пожалуйста, фио ребенка, возраст и контактный телефон.
Оплату можно произвести по реквизитам:

ГАУ «ИТ-парк»
Государственное автономное учреждение «Технопарк в сфере высоких технологий «ИТ-парк»
420074, г. Казань, ул. Петербургская, 52
ИНН 1655191213 / КПП 165501001
р/с 03224643920000001100
л/с № ЛАВ00707002- ИТпарк, 
в ОТДЕЛЕНИЕ-НБ РЕСПУБЛИКА ТАТАРСТАН БАНКА РОССИИ//УФК по Республике Татарстан г. Казань
БИК 019205400
ОГРН 1101690018760
ОКТМО - 92701000
КБК - 0
к/с 40102810445370000079 
Телефон / факс: 235-14-75
e-mail: it.park@tatar.ru

Или по QR - коду тинькофф или ак барс.
Чек пришлите в чат👌''', picture='pay_qr_code.jpg', keyboard=pay_keyboard)
