from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db import Session, Children
from app.states.children_list import ChildrenListStatesGroup
from app.states.parent import ParentStatesGroup
from states.common import cancel_button


async def get_children_list_keyboard(parent_id, callback_query: types.CallbackQuery):
    with Session() as session:
        children_list = session.query(Children).filter(Children.parent_id == parent_id).all()

        keyboard = InlineKeyboardMarkup(row_width=1)
        if not children_list:
            await callback_query.answer('Вы ещё не добавили ни одного ребенка')
            return
        for children in children_list:
            button = InlineKeyboardButton(f'{children.name} {children.surname[0]}.', callback_data=children.id)
            keyboard.add(button)
        return keyboard.row(cancel_button)


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await ParentStatesGroup.start.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await ChildrenListStatesGroup.previous()
    last_message = await ChildrenListStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def back_to_children_list(callback_query: types.CallbackQuery):
    return await start(callback_query)


async def start(callback_query: types.CallbackQuery):
    keyboard = await get_children_list_keyboard(callback_query.message.chat.id, callback_query)
    if keyboard:
        await ChildrenListStatesGroup.waiting_for_children.apply(
            callback_query=callback_query, message_text='Выберите ребенка', keyboard=keyboard)


async def entered_children(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(children_id=callback_query.data)

    with Session() as session:
        children = session.query(Children).filter(Children.id == callback_query.data).first()
        await ChildrenListStatesGroup.waiting_for_action.apply(
            message_text=f"Фамилия: {children.surname}\n"
                         f"Имя: {children.name}\n"
                         f"Отчество: {children.patronymic}\n"
                         f"Дата рождения: {children.date_of_birth}\n",
            callback_query=callback_query
        )


def register_handlers_children_list(dp: Dispatcher):
    dp.register_callback_query_handler(back_to_children_list, lambda c: c.data == 'back', state=ChildrenListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(back, lambda c: c.data == 'back', state=ChildrenListStatesGroup.all_states[2:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel', state=ChildrenListStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'children_list', state=ParentStatesGroup.start)
    dp.register_callback_query_handler(entered_children, state=ChildrenListStatesGroup.waiting_for_children)
