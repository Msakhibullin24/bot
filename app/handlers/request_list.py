from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db import Session, Children, Course, CourseGroup, Request
from app.states.children_list import ChildrenListStatesGroup
from config import TOKEN
from states.common import cancel_button
from states.request_list import RequestListStatesGroup

bot = Bot(token=TOKEN)


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await RequestListStatesGroup.previous()
    last_message = await RequestListStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        requests = session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course)\
            .filter(Request.children_id == data.get('children_id')).order_by(Course.name).all()
        if not requests:
            await callback_query.answer("Вы ещё отправляли заявки")
            return

        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
        for request in requests:
            request_button = InlineKeyboardButton(request.course_group.course.name, callback_data=request.course_group_id)
            keyboard.add(request_button)
    keyboard.row(cancel_button)
    await RequestListStatesGroup.waiting_for_request.apply(callback_query=callback_query, keyboard=keyboard)


async def entered_request(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(request_course_group_id=callback_query.data)
    data = await state.get_data()

    with Session() as session:
        request = session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course) \
            .filter(
                Request.course_group_id == data.get('request_course_group_id'),
                Request.children_id == data.get('children_id')
        ).order_by(Course.name).first()

        message_text = f'{request.children.name} {request.children.surname[0]}.\n' \
                       f'{request.course_group.course.name}\n' \
                       f'{request.course_group.name}\n'
        for timetable in request.course_group.course_group_timetables:
            message_text += f'{timetable.time} {timetable.weekday.value}\n'

        await RequestListStatesGroup.waiting_for_action.apply(message_text=message_text, callback_query=callback_query)


async def delete(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        request = session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course) \
            .filter(
                Request.course_group_id == data.get('request_course_group_id'),
                Request.children_id == data.get('children_id')
        ).order_by(Course.name).first()

        message_text = f'Действительно удалить заявку?\n' \
                       f'{request.children.name} {request.children.surname[0]}.\n' \
                       f'{request.course_group.course.name}\n' \
                       f'{request.course_group.name}\n'
        for timetable in request.course_group.course_group_timetables:
            message_text += f'{timetable.time} {timetable.weekday.value}\n'

        await RequestListStatesGroup.end.apply(message_text=message_text, message=callback_query.message)


async def end(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        request = session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course) \
            .filter(
                Request.course_group_id == data.get('request_course_group_id'),
                Request.children_id == data.get('children_id')
        ).order_by(Course.name).first()

        session.delete(request)
        session.commit()

        await state.finish()
        await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)
        state = Dispatcher.get_current().current_state()
        await state.update_data(children_id=data.get('children_id'))


def register_handlers_request_list(dp: Dispatcher):
    dp.register_callback_query_handler(back, lambda c: c.data == 'back', state=RequestListStatesGroup.all_states[1:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel', state=RequestListStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'children_request_list', state=ChildrenListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(entered_request, state=RequestListStatesGroup.waiting_for_request)
    dp.register_callback_query_handler(delete, lambda c: c.data == 'delete', state=RequestListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(end, lambda c: c.data == 'delete', state=RequestListStatesGroup.end)
