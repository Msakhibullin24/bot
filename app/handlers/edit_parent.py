from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import literal
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import PhoneNumber

from app.db import Session, Parent
from app.states.common import check_phone_number_is_valid, cancel_button, save_button
from app.states.edit_parent import EditParentStatesGroup
from app.states.parent import ParentStatesGroup


async def create_keyboard(state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(row_width=1)
    chosen_surname_button = InlineKeyboardButton(data.get('surname'), callback_data='chosen_surname')
    chosen_name_button = InlineKeyboardButton(data.get('name'), callback_data='chosen_name')
    chosen_patronymic_button = InlineKeyboardButton(data.get('patronymic'), callback_data='chosen_patronymic')
    chosen_phone_number_button = InlineKeyboardButton(str(data.get('phone_number')), callback_data='chosen_phone_number')
    keyboard.add(chosen_surname_button, chosen_name_button, chosen_patronymic_button, chosen_phone_number_button)
    keyboard.row(cancel_button, save_button)
    return keyboard


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await ParentStatesGroup.start.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    await EditParentStatesGroup.start.apply(callback_query=callback_query, keyboard=await create_keyboard(state))


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        parent = session.query(Parent).filter(Parent.id == callback_query.message.chat.id).first()
        await state.update_data(
            surname=parent.surname, name=parent.name, patronymic=parent.patronymic, phone_number=parent.phone_number
        )
    await EditParentStatesGroup.start.apply(callback_query=callback_query, keyboard=await create_keyboard(state))


async def chosen_surname(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditParentStatesGroup.waiting_for_surname.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_name(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditParentStatesGroup.waiting_for_name.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_patronymic(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditParentStatesGroup.waiting_for_patronymic.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_phone_number(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditParentStatesGroup.waiting_for_phone_number.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def entered_surname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(surname=message.text)
    await EditParentStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(name=message.text)
    await EditParentStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_patronymic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(patronymic=message.text)
    await EditParentStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    if not check_phone_number_is_valid(message.text):
        await message.answer(f'Номер телефона {message.text} невалидный')
        last_message = await EditParentStatesGroup.waiting_for_phone_number.apply(message=message)
        await state.update_data(last_message=last_message)
        return

    phone_number = PhoneNumber(message.text, 'RU')
    with Session() as session:
        q = session.query(Parent).filter(Parent.phone_number == phone_number)
        if session.query(literal(True)).filter(q.exists()).scalar():
            await message.answer(f'Номер телефона {phone_number} уже существует')
            last_message = await EditParentStatesGroup.waiting_for_phone_number.apply(message=message)
            await state.update_data(last_message=last_message)
            return

    await state.update_data(phone_number=phone_number)
    await EditParentStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def save(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        parent = session.query(Parent).filter(Parent.id == callback_query.message.chat.id).first()
        if not parent:
            await callback_query.message.answer("Ошибка")
        changed = any(
            [parent.surname != data.get('surname'), parent.name != data.get('name'),
             parent.patronymic != data.get('patronymic'), parent.phone_number != data.get('phone_number')]
        )
        parent.surname = data.get('surname')
        parent.name = data.get('name')
        parent.patronymic = data.get('patronymic')
        parent.phone_number = data.get('phone_number')

        try:
            session.commit()
        except IntegrityError:
            await callback_query.message.answer("Ошибка")

        if changed:
            await callback_query.message.edit_text(
                f"Родитель отредактирован: \n"
                f"Фамилия: {parent.surname}\n"
                f"Имя: {parent.name}\n"
                f"Отчество: {parent.patronymic}\n"
                f"Номер телефона: {parent.phone_number}\n"
            )
    await state.finish()
    await ParentStatesGroup.start.apply(message=callback_query.message)


def register_handlers_edit_parent(dp: Dispatcher):
    dp.register_callback_query_handler(
        back, lambda c: c.data == 'back', state=EditParentStatesGroup.all_states[1:])
    dp.register_callback_query_handler(
        cancel, lambda c: c.data == 'cancel', state=EditParentStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'edit_parent', state=ParentStatesGroup.start)

    dp.register_callback_query_handler(
        chosen_surname, lambda c: c.data == 'chosen_surname', state=EditParentStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_name, lambda c: c.data == 'chosen_name', state=EditParentStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_patronymic, lambda c: c.data == 'chosen_patronymic', state=EditParentStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_phone_number, lambda c: c.data == 'chosen_phone_number', state=EditParentStatesGroup.start)

    dp.register_message_handler(entered_surname, state=EditParentStatesGroup.waiting_for_surname)
    dp.register_message_handler(entered_name, state=EditParentStatesGroup.waiting_for_name)
    dp.register_message_handler(entered_patronymic, state=EditParentStatesGroup.waiting_for_patronymic)
    dp.register_message_handler(entered_phone_number, state=EditParentStatesGroup.waiting_for_phone_number)

    dp.register_callback_query_handler(save, lambda c: c.data == 'save', state=EditParentStatesGroup.start)
