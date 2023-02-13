from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy import literal
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import PhoneNumber

from app.db import Session, Parent
from app.states.common import StartStatesGroup, check_phone_number_is_valid
from app.states.parent import ParentStatesGroup
from app.states.registration import RegistrationParentStatesGroup


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await StartStatesGroup.start.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await RegistrationParentStatesGroup.previous()
    last_message = await RegistrationParentStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await RegistrationParentStatesGroup.waiting_for_surname.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def entered_surname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(surname=message.text)
    last_message = await RegistrationParentStatesGroup.waiting_for_name.apply(message=message)

    await state.update_data(last_message=last_message)


async def entered_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(name=message.text)
    last_message = await RegistrationParentStatesGroup.waiting_for_patronymic.apply(message=message)

    await state.update_data(last_message=last_message)


async def entered_patronymic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(patronymic=message.text)
    last_message = await RegistrationParentStatesGroup.waiting_for_phone_number.apply(message=message)

    await state.update_data(last_message=last_message)


async def entered_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    if not check_phone_number_is_valid(message.text):
        await message.answer(f'Номер телефона {message.text} невалидный')
        last_message = await RegistrationParentStatesGroup.waiting_for_phone_number.apply(message=message)
        await state.update_data(last_message=last_message)
        return

    phone_number = PhoneNumber(message.text, 'RU')
    with Session() as session:
        q = session.query(Parent).filter(Parent.phone_number == phone_number)
        if session.query(literal(True)).filter(q.exists()).scalar():
            await message.answer(f'Номер телефона {phone_number} уже существует')
            last_message = await RegistrationParentStatesGroup.waiting_for_phone_number.apply(message=message)
            await state.update_data(last_message=last_message)
            return

    await state.update_data(phone_number=phone_number)
    data = await state.get_data()

    await RegistrationParentStatesGroup.end.apply(
        message_text=f"Фамилия: {data.get('surname')}\n"
                     f"Имя: {data.get('name')}\n"
                     f"Отчество: {data.get('patronymic')}\n"
                     f"Номер телефона: {data.get('phone_number')}\n"
                     f"Создать?",
        message=message
    )


async def end(callback_query: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        data = await state.get_data()
        parent = Parent(id=callback_query.from_user.id, surname=data.get('surname'), name=data.get('name'),
                        patronymic=data.get('patronymic'), phone_number=data.get('phone_number'))
        session.add(parent)
        try:
            session.commit()
        except IntegrityError:
            await callback_query.message.answer(
                f'Родитель с номером телефона {data.get("phone_number")} уже зарегистрирован')
        await callback_query.message.edit_text(
            f"Родитель создан: \n"
            f"Surname: {parent.surname}\n"
            f"Name: {parent.name}\n"
            f"Patronymic: {parent.patronymic}\n"
            f"Phone Number: {parent.phone_number}\n"
        )

    await state.finish()
    await ParentStatesGroup.start.apply(callback_query=callback_query)


def register_handlers_registration(dp: Dispatcher):
    dp.register_callback_query_handler(back, lambda c: c.data == 'back',
                                       state=RegistrationParentStatesGroup.all_states[1:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel',
                                       state=RegistrationParentStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'registration', state=StartStatesGroup.start)

    dp.register_message_handler(entered_surname, state=RegistrationParentStatesGroup.waiting_for_surname)
    dp.register_message_handler(entered_name, state=RegistrationParentStatesGroup.waiting_for_name)
    dp.register_message_handler(entered_patronymic, state=RegistrationParentStatesGroup.waiting_for_patronymic)
    dp.register_message_handler(entered_phone_number, state=RegistrationParentStatesGroup.waiting_for_phone_number)
    dp.register_callback_query_handler(end, lambda c: c.data == 'create', state=RegistrationParentStatesGroup.end)
