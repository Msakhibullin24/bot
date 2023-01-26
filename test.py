from datetime import time

from sqlalchemy_utils import PhoneNumber

from db import Parent, Session, Children, Course, CourseGroup, CourseGroupTimetable, WeekDaysEnum, Request, \
    PaymentStatusEnum
from db import Session

def create_parent():
    with Session() as session:
        # Создаю Родителя
        # parent = Parent(id=600)

        # Сохраняю его
        # session.add(parent)
        # session.commit()

        p = session.query(Parent).filter(Parent.id == 600).first()
        p.name = '123'

        print(p)

        session.add(p)
        session.commit()


def create_children():
    with Session() as session:
        # Создаю Родителя
        parent = Parent(id=123, name='name', surname='surname', patronymic='patronymic', phone_number=PhoneNumber('1232434530', 'RU'))

        # Создаю Ребенка, указываю ему родителя сверху
        children = Children(name='name', surname='surname', patronymic='patronymic', age=8, parent=parent)

        # Сохраняю все
        session.add_all([parent, children])
        session.commit()


def create_course():
    # Основы программирования. Кодвардс (6+)
    # Продолжительность занятия — 90 минут
    # Стоимость — 4 400 ₽ в месяц
    with Session() as session:
        # Создаю курс
        course = Course(name='Основы программирования. Кодвардс', price=4400, duration=90, age=6)

        # Сохраняю
        session.add(course)
        session.commit()


def create_course_group_with_timetable():
    # Перекладная мультипликация (6+)
    # 🔶 1 группа: пн 18:00 и пт 18:00
    # 🔷 2 группа: чт 18:00 и сб 18:00
    # Продолжительность 1 занятия — 120 минут
    # Стоимость — 8 800 ₽ в месяц
    with Session() as session:
        # Создаю курс
        course = Course(name='Перекладная мультипликация', price=8800, duration=120, age=6)

        # Создаю первую группу, указываю курс сверху
        course_group1 = CourseGroup(name='1 группа', free_places=10, course=course)

        # Создаю дни, в которые проводятся занятие в этой группе, указываю первую группу
        course_group_timetable11 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.monday, course_group=course_group1)
        course_group_timetable12 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.friday, course_group=course_group1)

        # Создаю вторую группу, указываю курс сверху
        course_group2 = CourseGroup(name='2 группа', free_places=20, course=course)

        # Создаю дни, в которые проводятся занятие в этой группе, указываю вторую группу
        course_group_timetable21 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.thursday, course_group=course_group2)
        course_group_timetable22 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.saturday, course_group=course_group2)

        # Сохраняю все
        session.add_all([
            course,
            course_group1, course_group_timetable11, course_group_timetable12,
            course_group2, course_group_timetable21, course_group_timetable22
        ])
        session.commit()


# def create_web_design():


def create_request():
    # Видеограф-клипмейкер (12+)
    # 🔶 1 группа: вт 18:00 и сб 18:00
    # Продолжительность занятия — 90 минут
    # Стоимость — 8 800 ₽ в месяц
    with Session() as session:
        # Создаю Родителя и Ребенка
        parent = Parent(id=456, name='name', surname='surname', patronymic='patronymic', phone_number=PhoneNumber('4321434530', 'RU'))
        children = Children(name='name', surname='surname', patronymic='patronymic', age=8, parent=parent)

        # Создаю курс
        course = Course(name='Видеограф-клипмейкер', price=8800, duration=90, age=12)
        # Создаю группу
        course_group1 = CourseGroup(name='1 группа', free_places=10, course=course)
        # Добавляю к группе дни, в которые проводятся занятия
        course_group_timetable11 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.tuesday, course_group=course_group1)
        course_group_timetable12 = CourseGroupTimetable(time=time(hour=18, minute=0), weekday=WeekDaysEnum.saturday, course_group=course_group1)

        # Создаю запрос на обучение ребенка в группе
        #     PaymentStatusEnum.checked - оплата проверена
        #     PaymentStatusEnum.no_checked - оплата не проверена
        #     PaymentStatusEnum.no_payment - не оплачено
        request = Request(payment_status=PaymentStatusEnum.no_payment, course_group=course_group1, children=children)

        # Сохраняю все
        session.add_all([parent, children, course, course_group1, course_group_timetable11, course_group_timetable12, request])
        session.commit()


def get_all_courses():
    with Session() as session:
        print(session.query(Course).all())


if __name__ == '__main__':
    create_parent()
