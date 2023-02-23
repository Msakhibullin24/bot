from aiogram.dispatcher.filters.state import StatesGroup

from app.states.common import CustomState


class MasterClassListStatesGroup(StatesGroup):
    waiting_for_course = CustomState(message_text='Выберите мастер класс')
    waiting_for_group = CustomState(message_text='Выберите группу')
    end = CustomState(message_text='Всё верно?')
