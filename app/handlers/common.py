from aiogram import types, Dispatcher

from app.db import Session, Parent
from app.states.common import StartStatesGroup
from app.states.parent import ParentStatesGroup


async def start_command(message: types.Message):
    with Session() as session:
        parent = session.query(Parent).filter_by(id=message.chat.id).one_or_none()
        if parent:
            await message.answer(
                f"Вы уже зарегистрированы как: {parent.surname} {parent.name} {parent.patronymic},"
                f" {parent.phone_number}\n"
            )
            await ParentStatesGroup.start.apply(message=message)
            return
    await StartStatesGroup.start.apply(message=message)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'], state='*')
