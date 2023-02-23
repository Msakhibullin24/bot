from datetime import date

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db import Session, Children, Course, CourseGroup, Request
from app.states.children_list import ChildrenListStatesGroup
from config import COURSES_PAGE_SIZE, TOKEN
from states.common import cancel_button, previous_button, next_button, back_button
from states.master_class_list import MasterClassListStatesGroup

bot = Bot(token=TOKEN)


def calculate_age(born):
    today = date.today()
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        birthday = born.replace(year=today.year,
                                month=born.month + 1, day=1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


def get_courses(session, age, page=0):
    return session.query(Course).filter(Course.is_master_class == True).filter(age >= Course.age).order_by(Course.name).limit(COURSES_PAGE_SIZE).offset(COURSES_PAGE_SIZE * page).all()


def get_keyboard_of_courses(courses) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for course in courses:
        course_button = InlineKeyboardButton(course.name, callback_data=course.id)
        keyboard.row(course_button)
    return keyboard


async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)


async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    if current_state.split(':')[-1] == 'waiting_for_group':
        messages_to_delete = data.get('messages_to_delete')
        if messages_to_delete:
            for message_id in messages_to_delete[:-1]:
                await bot.delete_message(callback_query.message.chat.id, message_id)
        return await start(callback_query, state)
    current_state = await MasterClassListStatesGroup.previous()
    last_message = await MasterClassListStatesGroup().__getattribute__(current_state.split(':')[-1]). \
        apply(callback_query=callback_query)
    await state.update_data(last_message=last_message)


async def start(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(page=0)
    data = await state.get_data()
    with Session() as session:
        children_id = data.get('children_id')
        children = session.query(Children).filter(Children.id == children_id).first()
        age = calculate_age(children.date_of_birth)
        await state.update_data(age=age)

        courses = get_courses(session, age=age)
        if not courses:
            await callback_query.answer("Нет мастер классов для вашего ребенка")
            return

        keyboard: InlineKeyboardMarkup = get_keyboard_of_courses(courses)
        courses_count = session.query(Course).filter(Course.is_master_class == True).filter(age >= Course.age).count()

    if courses_count > len(courses):
        keyboard.row(next_button)
    keyboard.row(cancel_button)
    await MasterClassListStatesGroup.waiting_for_course.apply(callback_query=callback_query, keyboard=keyboard)


async def next_list(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page') + 1
    age = data.get('age')

    with Session() as session:
        count = session.query(Course).filter(Course.is_master_class == False).filter(age >= Course.age).count()
        courses = get_courses(session, age=age, page=page)
        keyboard: InlineKeyboardMarkup = get_keyboard_of_courses(courses)

    await state.update_data(page=page)

    if count - COURSES_PAGE_SIZE * (page + 1) > 0:
        keyboard.row(previous_button, next_button)
    else:
        keyboard.row(previous_button)
    keyboard.row(cancel_button)
    await MasterClassListStatesGroup.waiting_for_course.apply(callback_query=callback_query, keyboard=keyboard)


async def previous_list(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page') - 1
    with Session() as session:
        courses = get_courses(session, age=data.get('age'), page=page)
        keyboard: InlineKeyboardMarkup = get_keyboard_of_courses(courses)

    await state.update_data(page=page)

    if page > 0:
        keyboard.row(previous_button, next_button)
    else:
        keyboard.row(next_button)
    keyboard.row(cancel_button)
    await MasterClassListStatesGroup.waiting_for_course.apply(callback_query=callback_query, keyboard=keyboard)


async def entered_course(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(course_id=callback_query.data)
    data = await state.get_data()
    with Session() as session:
        groups = session.query(CourseGroup).filter(CourseGroup.free_places > 0).filter(CourseGroup.course_id == callback_query.data)\
            .join(CourseGroup.course_group_timetables).all()
        if not groups:
            await callback_query.answer("Нет свободных групп")
            return

        request = session.query(Request).\
            filter(
                Request.course_group_id.in_([group.id for group in groups]),
                Request.children_id == data.get('children_id')
            ).first()

        if request:
            await callback_query.answer("Заявка на этот курс уже отправлена")
            return

        messages = []
        message = await MasterClassListStatesGroup.waiting_for_group.apply(message=callback_query.message)
        messages.append(message.message_id)

        await callback_query.message.delete()
        for group in groups[:-1]:
            message_text = f'{group.name}\n'
            for timetable in group.course_group_timetables:
                message_text += f'{timetable.time.strftime("%H:%M")} {timetable.weekday.value}\n'
            keyboard = InlineKeyboardMarkup()
            request_button = InlineKeyboardButton('Выбрать', callback_data=group.id)
            keyboard.row(request_button)
            message = await callback_query.message.answer(message_text, reply_markup=keyboard)
            messages.append(message.message_id)

        message_text = f'{groups[-1].name}\n'
        for timetable in groups[-1].course_group_timetables:
            message_text += f'{timetable.time.strftime("%H:%M")} {timetable.weekday.value}\n'
        keyboard = InlineKeyboardMarkup()
        request_button = InlineKeyboardButton('Выбрать', callback_data=groups[-1].id)
        keyboard.row(back_button, cancel_button, request_button)
        message = await callback_query.message.answer(message_text, reply_markup=keyboard)
        messages.append(message.message_id)

    await state.update_data(messages_to_delete=messages)


async def entered_group(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(group_id=callback_query.data)
    data = await state.get_data()
    for message_id in data.get('messages_to_delete'):
        await bot.delete_message(callback_query.message.chat.id, message_id)

    with Session() as session:
        children = session.query(Children).filter(Children.id == data.get('children_id')).first()
        group = session.query(CourseGroup).filter(CourseGroup.id == data.get('group_id')).join(CourseGroup.course)\
            .join(CourseGroup.course_group_timetables).first()

        if not group:
            await callback_query.answer("В группе нет места")
            return

        message_text = f'{children.name} {children.surname[0]}.\n' \
                       f'{group.course.name}\n' \
                       f'{group.name}\n'
        for timetable in group.course_group_timetables:
            message_text += f'{timetable.time.strftime("%H:%M")} {timetable.weekday.value}\n'

        keyboard = InlineKeyboardMarkup()
        request_button = InlineKeyboardButton('Записаться', callback_data=group.id)
        keyboard.row(back_button, cancel_button, request_button)
        await MasterClassListStatesGroup.end.apply(message_text=message_text, message=callback_query.message, keyboard=keyboard)


async def end(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(group_id=callback_query.data)
    data = await state.get_data()

    with Session() as session:
        children = session.query(Children).filter(Children.id == data.get('children_id')).first()
        group = session.query(CourseGroup).filter(CourseGroup.id == data.get('group_id')).join(CourseGroup.course)\
            .join(CourseGroup.course_group_timetables).first()

        if not group:
            await callback_query.answer("В группе нет места")
            return

        request = Request(children=children, course_group=group)
        session.add(request)
        session.commit()

        await state.finish()
        await ChildrenListStatesGroup.waiting_for_action.apply(callback_query=callback_query)
        state = Dispatcher.get_current().current_state()
        await state.update_data(children_id=data.get('children_id'))


def register_handlers_master_class_list(dp: Dispatcher):
    dp.register_callback_query_handler(back, lambda c: c.data == 'back', state=MasterClassListStatesGroup.all_states[1:])
    dp.register_callback_query_handler(cancel, lambda c: c.data == 'cancel', state=MasterClassListStatesGroup.all_states)

    dp.register_callback_query_handler(start, lambda c: c.data == 'master_class_list', state=ChildrenListStatesGroup.waiting_for_action)
    dp.register_callback_query_handler(next_list, lambda c: c.data == 'next', state=MasterClassListStatesGroup.waiting_for_course)
    dp.register_callback_query_handler(previous_list, lambda c: c.data == 'previous', state=MasterClassListStatesGroup.waiting_for_course)
    dp.register_callback_query_handler(entered_course, state=MasterClassListStatesGroup.waiting_for_course)
    dp.register_callback_query_handler(entered_group, state=MasterClassListStatesGroup.waiting_for_group)
    dp.register_callback_query_handler(end, state=MasterClassListStatesGroup.end)
