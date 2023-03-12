from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db import Session, Course, CourseGroup, Request, RequestFile, PaymentStatusEnum
from app.states.children_list import ChildrenListStatesGroup
from config import TOKEN
from states.common import cancel_button
from states.request_list import RequestListStatesGroup

bot = Bot(token=TOKEN)


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state.split(':')[-1] == 'pay':
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await ChildrenListStatesGroup.waiting_for_action.apply(message=callback_query.message)
    else:
        await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state.split(':')[-1] == 'waiting_for_action':
        return await start(callback_query, state)

    elif current_state.split(':')[-1] == 'pay':
        await callback_query.message.edit_reply_markup(reply_markup=None)
        return await RequestListStatesGroup.waiting_for_action.apply(message=callback_query.message)

    current_state = await RequestListStatesGroup.previous()
    last_message = await RequestListStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        requests = session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course) \
            .filter(Request.children_id == data.get('children_id')).order_by(Course.name).all()
        if not requests:
            await callback_query.answer("Вы ещё отправляли заявки")
            return

        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
        for request in requests:
            request_button = InlineKeyboardButton(request.course_group.course.name, callback_data=request.id)
            keyboard.add(request_button)
    keyboard.row(cancel_button)
    await RequestListStatesGroup.waiting_for_request.apply(callback_query=callback_query, keyboard=keyboard)


async def entered_request(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(request_id=callback_query.data)
    data = await state.get_data()

    with Session() as session:
        request = get_request(session, data.get('request_id'))
        message_text = get_request_info(request)
        await RequestListStatesGroup.waiting_for_action.apply(message_text=message_text, callback_query=callback_query)


async def delete(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        request = get_request(session, data.get('request_id'))

        message_text = f'Действительно удалить заявку?\n' \
                       f'{request.children.name} {request.children.surname[0]}.\n' \
                       f'{request.course_group.course.name}\n' \
                       f'{request.course_group.name}\n'
        for timetable in request.course_group.course_group_timetables:
            message_text += f'{timetable.time} {timetable.weekday.value}\n'

        await RequestListStatesGroup.delete.apply(message_text=message_text, callback_query=callback_query)


async def end_delete(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    with Session() as session:
        request = get_request(session, data.get('request_id'))

        session.delete(request)
        session.commit()

        await state.finish()
        await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)
        state = Dispatcher.get_current().current_state()
        await state.update_data(children_id=data.get('children_id'))


async def pay(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')
    with Session() as session:
        request = get_request(session, request_id)
        if request.payment_status == PaymentStatusEnum.success:
            return await callback_query.answer('Оплата уже произведена')
        elif request.payment_status == PaymentStatusEnum.no_checked:
            return await callback_query.answer('Оплата находится на проверке')

    await RequestListStatesGroup.pay.apply(callback_query=callback_query)


async def wait_for_photo(message: types.Message, state: FSMContext):
    destination = await message.photo[-1].download()
    data = await state.get_data()
    write_file_to_db(data.get('request_id'), destination.name)
    await message.answer('Документы на проверке')
    with Session() as session:
        request = get_request(session, data.get('request_id'))
        request.payment_status = PaymentStatusEnum.no_checked
        session.commit()
        message_text = get_request_info(request)
    await RequestListStatesGroup.waiting_for_action.apply(message_text=message_text, message=message)


async def wait_for_file(message: types.Message, state: FSMContext):
    destination = await message.document.download()
    data = await state.get_data()
    write_file_to_db(data.get('request_id'), destination.name)
    await message.answer('Документы на проверке')
    with Session() as session:
        request = get_request(session, data.get('request_id'))
        request.payment_status = PaymentStatusEnum.no_checked
        session.commit()
        message_text = get_request_info(request)
    await RequestListStatesGroup.waiting_for_action.apply(message_text=message_text, message=message)


def get_request_info(request):
    message_text = f'{request.children.name} {request.children.surname[0]}.\n' \
                   f'{request.course_group.course.name}\n' \
                   f'{request.course_group.name}\n' \
                   f'Статус оплаты: {request.payment_status.value}\n'
    for timetable in request.course_group.course_group_timetables:
        message_text += f'{timetable.weekday.value}, {timetable.time.strftime("%H:%M")}\n'
    return message_text


def write_file_to_db(request_id, path):
    with Session() as session:
        file = RequestFile(request_id=request_id, file=path)
        session.add(file)
        session.commit()


def get_request(session, request_id):
    return session.query(Request).join(Request.children).join(Request.course_group).join(CourseGroup.course) \
        .filter(
        Request.id == request_id
    ).first()


def register_handlers_request_list(dp: Dispatcher):
    dp.register_callback_query_handler(back, lambda c: c.data == 'back', state=RequestListStatesGroup.all_states[1:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel', state=RequestListStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'children_request_list',
                                       state=ChildrenListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(entered_request, state=RequestListStatesGroup.waiting_for_request)
    dp.register_callback_query_handler(delete, lambda c: c.data == 'delete',
                                       state=RequestListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(end_delete, lambda c: c.data == 'delete', state=RequestListStatesGroup.delete)
    dp.register_callback_query_handler(pay, lambda c: c.data == 'pay', state=RequestListStatesGroup.waiting_for_action)
    dp.register_message_handler(wait_for_photo, content_types=['photo'], state=RequestListStatesGroup.pay)
    dp.register_message_handler(wait_for_file, content_types=['document'], state=RequestListStatesGroup.pay)
