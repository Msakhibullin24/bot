from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import IntegrityError

from app.db import Session, Children
from app.states.common import check_date_of_birth_is_valid, cancel_button, save_button, delete_button, back_button
from app.states.edit_children import EditChildrenStatesGroup
from app.states.children_list import ChildrenListStatesGroup
from handlers.children_list import get_children_list_keyboard


async def create_keyboard(state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(row_width=1)
    chosen_surname_button = InlineKeyboardButton(data.get('surname'), callback_data='chosen_surname')
    chosen_name_button = InlineKeyboardButton(data.get('name'), callback_data='chosen_name')
    chosen_patronymic_button = InlineKeyboardButton(data.get('patronymic'), callback_data='chosen_patronymic')
    chosen_date_of_birth_button = InlineKeyboardButton(str(data.get('date_of_birth')),
                                                       callback_data='chosen_date_of_birth')
    keyboard.add(chosen_surname_button, chosen_name_button, chosen_patronymic_button, chosen_date_of_birth_button)
    keyboard.row(back_button, cancel_button, save_button, delete_button)
    return keyboard


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await ChildrenListStatesGroup.waiting_for_children.apply(
        callback_query=callback_query,
        keyboard=await get_children_list_keyboard(callback_query.message.chat.id, callback_query)
    )


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    await EditChildrenStatesGroup.start.apply(callback_query=callback_query, keyboard=await create_keyboard(state))


async def back_to_actions(callback_query: types.CallbackQuery):
    await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        children = session.query(Children).filter(Children.id == data.get('children_id')).first()
        await state.update_data(
            surname=children.surname, name=children.name, patronymic=children.patronymic,
            date_of_birth=children.date_of_birth
        )
    await EditChildrenStatesGroup.start.apply(callback_query=callback_query, keyboard=await create_keyboard(state))


async def chosen_surname(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditChildrenStatesGroup.waiting_for_surname.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_name(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditChildrenStatesGroup.waiting_for_name.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_patronymic(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditChildrenStatesGroup.waiting_for_patronymic.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def chosen_date_of_birth(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await EditChildrenStatesGroup.waiting_for_date_of_birth.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def entered_surname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(surname=message.text)
    await EditChildrenStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(name=message.text)
    await EditChildrenStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_patronymic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    await state.update_data(patronymic=message.text)
    await EditChildrenStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def entered_date_of_birth(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data.get('last_message').delete_reply_markup()

    date = message.text.strip().replace(' ', '')
    if not check_date_of_birth_is_valid(date):
        await message.answer(f'Дата {message.text} указана неверно')
        last_message = await EditChildrenStatesGroup.waiting_for_date_of_birth.apply(message=message)
        await state.update_data(last_message=last_message)
        return

    await state.update_data(date_of_birth=date)
    await EditChildrenStatesGroup.start.apply(message=message, keyboard=await create_keyboard(state))


async def save(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        children = session.query(Children).filter(Children.id == data.get('children_id')).first()
        if not children:
            await callback_query.message.answer("Ошибка")

        changed = any(
            [children.surname != data.get('surname'), children.name != data.get('name'),
             children.patronymic != data.get('patronymic'), children.date_of_birth != data.get('date_of_birth')]
        )
        surname = data.get('surname')
        name = data.get('name')
        patronymic = data.get('patronymic')
        date_of_birth = data.get('date_of_birth')

        children.surname = surname if surname else children.surname
        children.name = name if name else children.name
        children.patronymic = patronymic if patronymic else children.patronymic
        children.date_of_birth = date_of_birth if date_of_birth else children.date_of_birth

        try:
            session.commit()
        except IntegrityError:
            await callback_query.message.answer("Ошибка")

        if changed:
            await callback_query.message.edit_text(
                f"Ребенок отредактирован: \n"
                f"Фамилия: {children.surname}\n"
                f"Имя: {children.name}\n"
                f"Отчество: {children.patronymic}\n"
                f"Дата рождения: {children.date_of_birth}\n"
            )
    await state.finish()
    await ChildrenListStatesGroup.waiting_for_children.apply(
        message=callback_query.message,
        keyboard=await get_children_list_keyboard(callback_query.message.chat.id, callback_query)
    )


async def chosen_delete(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    last_message = await EditChildrenStatesGroup.waiting_for_delete.apply(
        message_text=f"Фамилия: {data['surname']}\n"
                     f"Имя: {data['name']}\n"
                     f"Отчество: {data['patronymic']}\n"
                     f"Дата рождения: {data['date_of_birth']}\n"
                     f"Удалить?",
        callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def delete(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        children = session.query(Children).filter(Children.id == data.get('children_id')).first()
        session.delete(children)
        try:
            session.commit()
        except IntegrityError:
            await callback_query.message.answer("Ошибка")

    await ChildrenListStatesGroup.waiting_for_children.apply(
        message=callback_query.message,
        keyboard=await get_children_list_keyboard(callback_query.message.chat.id, callback_query)
    )


def register_handlers_edit_children(dp: Dispatcher):
    dp.register_callback_query_handler(
        back, lambda c: c.data == 'back', state=EditChildrenStatesGroup.all_states[1:])
    dp.register_callback_query_handler(
        back_to_actions, lambda c: c.data == 'back', state=EditChildrenStatesGroup.all_states[0])
    dp.register_callback_query_handler(
        cancel, lambda c: c.data == 'cancel', state=EditChildrenStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'edit_children',
                                       state=ChildrenListStatesGroup.waiting_for_action)

    dp.register_callback_query_handler(
        chosen_surname, lambda c: c.data == 'chosen_surname', state=EditChildrenStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_name, lambda c: c.data == 'chosen_name', state=EditChildrenStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_patronymic, lambda c: c.data == 'chosen_patronymic', state=EditChildrenStatesGroup.start)
    dp.register_callback_query_handler(
        chosen_date_of_birth, lambda c: c.data == 'chosen_date_of_birth', state=EditChildrenStatesGroup.start)

    dp.register_message_handler(entered_surname, state=EditChildrenStatesGroup.waiting_for_surname)
    dp.register_message_handler(entered_name, state=EditChildrenStatesGroup.waiting_for_name)
    dp.register_message_handler(entered_patronymic, state=EditChildrenStatesGroup.waiting_for_patronymic)
    dp.register_message_handler(entered_date_of_birth, state=EditChildrenStatesGroup.waiting_for_date_of_birth)

    dp.register_callback_query_handler(save, lambda c: c.data == 'save', state=EditChildrenStatesGroup.start)

    dp.register_callback_query_handler(
        chosen_delete, lambda c: c.data == 'delete', state=EditChildrenStatesGroup.start)
    dp.register_callback_query_handler(
        delete, lambda c: c.data == 'delete', state=EditChildrenStatesGroup.waiting_for_delete)
