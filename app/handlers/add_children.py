from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext

from app import config
from app.db import Session, Children
from app.states.add_children import AddChildrenStatesGroup
from app.states.common import check_date_of_birth_is_valid
from app.states.parent import ParentStatesGroup

bot = Bot(token=config.TOKEN)


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await ParentStatesGroup.start.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await AddChildrenStatesGroup.previous()
    last_message = await AddChildrenStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    last_message = await AddChildrenStatesGroup.waiting_for_surname.apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def entered_surname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data['last_message'].delete_reply_markup()

    await state.update_data(surname=message.text)
    last_message = await AddChildrenStatesGroup.waiting_for_name.apply(message=message)

    await state.update_data(last_message=last_message)


async def entered_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data['last_message'].delete_reply_markup()

    await state.update_data(name=message.text)
    last_message = await AddChildrenStatesGroup.waiting_for_patronymic.apply(message=message)

    await state.update_data(last_message=last_message)


async def entered_patronymic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data['last_message'].delete_reply_markup()

    await state.update_data(patronymic=message.text)
    last_message = await AddChildrenStatesGroup.waiting_for_date_of_birth.apply(message=message)
    await state.update_data(last_message=last_message)


async def entered_date_of_birth(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await data['last_message'].delete_reply_markup()

    date = message.text.strip().replace(' ', '')
    if not check_date_of_birth_is_valid(date):
        await message.answer(f'Дата {message.text} указана неверно')
        last_message = await AddChildrenStatesGroup.waiting_for_date_of_birth.apply(message=message)
        await state.update_data(last_message=last_message)
        return

    await state.update_data(date_of_birth=date)
    data = await state.get_data()

    last_message = await AddChildrenStatesGroup.end.apply(
        message_text=f"Фамилия: {data['surname']}\n"
                     f"Имя: {data['name']}\n"
                     f"Отчество: {data['patronymic']}\n"
                     f"Дата рождения: {data['date_of_birth']}\n"
                     f"Создать?",
        message=message)
    await state.update_data(last_message=last_message)


async def end(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await data['last_message'].delete_reply_markup()

    with Session() as session:
        data = await state.get_data()
        children = Children(surname=data['surname'], name=data['name'], patronymic=data['patronymic'],
                            date_of_birth=data['date_of_birth'], parent_id=callback_query.message.chat.id)
        session.add(children)
        session.commit()
        await callback_query.message.edit_text(
            f"Создан ребенок\n"
            f"Фамилия: {children.surname}\n"
            f"Имя: {children.name}\n"
            f"Отчество: {children.patronymic}\n"
            f"Дата рождения: {children.date_of_birth}\n"
        )
    await state.finish()
    await ParentStatesGroup.start.apply(message=callback_query.message)


def register_handlers_add_children(dp: Dispatcher):
    dp.register_callback_query_handler(back, lambda c: c.data == 'back', state=AddChildrenStatesGroup.all_states[1:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel', state=AddChildrenStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'add_children', state=ParentStatesGroup.start)
    dp.register_message_handler(entered_surname, state=AddChildrenStatesGroup.waiting_for_surname)
    dp.register_message_handler(entered_name, state=AddChildrenStatesGroup.waiting_for_name)
    dp.register_message_handler(entered_patronymic, state=AddChildrenStatesGroup.waiting_for_patronymic)
    dp.register_message_handler(entered_date_of_birth, state=AddChildrenStatesGroup.waiting_for_date_of_birth)
    dp.register_callback_query_handler(end, lambda c: c.data == 'create', state=AddChildrenStatesGroup.end)
