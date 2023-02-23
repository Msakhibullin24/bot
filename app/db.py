import enum

from sqlalchemy import Column, Integer, String, func, DateTime, ForeignKey, CheckConstraint, TIME, PrimaryKeyConstraint, \
    Enum, create_engine, Date, BigInteger, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, validates
from sqlalchemy_utils import PhoneNumberType

from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}', future=True, hide_parameters=True)

engine.connect()
Session = sessionmaker()
Session.configure(bind=engine)


Base = declarative_base()


class PaymentStatusEnum(enum.Enum):
    checked = 'Оплата подтверждена'
    no_checked = 'Оплата произведена'
    no_payment = 'Не оплачено'


class WeekDaysEnum(enum.Enum):
    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    thursday = 'Четверг'
    friday = 'Пятница'
    saturday = 'Суббота'
    sunday = 'Воскресенье'


class BaseMixin(object):
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Parent(Base):
    __tablename__ = "parent"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    phone_number = Column(PhoneNumberType(), unique=True)

    children = relationship("Children", back_populates="parent")

    @validates('name', 'surname', 'patronymic')
    def convert_capitalize(self, key, value):
        return value.capitalize()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"surname='{self.surname}', "
            f"phone_number='{self.phone_number}')>"
        )


class Children(Base, BaseMixin):
    __tablename__ = "children"

    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
    date_of_birth = Column(Date, )
    parent_id = Column(BigInteger, ForeignKey("parent.id"))

    parent = relationship("Parent", back_populates="children")
    requests = relationship("Request", back_populates="children")

    @validates('name', 'surname', 'patronymic')
    def convert_capitalize(self, key, value):
        return value.capitalize()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"surname='{self.surname}', "
            f"date_of_birth='{self.date_of_birth}',"
            f"parent_id='{self.parent_id}')>"
        )


class Course(Base, BaseMixin):
    __tablename__ = "course"
    __table_args__ = (
        CheckConstraint('price >= 0'),
        CheckConstraint('duration >= 0'),
        CheckConstraint('age > 0'),
        CheckConstraint('age < 100'),
    )

    name = Column(String, unique=True)
    price = Column(Integer)
    duration = Column(Integer)
    age = Column(Integer)
    is_master_class = Column(Boolean, default=True)

    course_groups = relationship("CourseGroup", back_populates="course")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"price='{self.price}', "
            f"duration='{self.duration}',"
            f"age='{self.age}')>"
        )


class CourseGroup(Base, BaseMixin):
    __tablename__ = "course_group"
    __table_args__ = (
        CheckConstraint('free_places >= 0'),
    )

    name = Column(String)
    free_places = Column(Integer)
    course_id = Column(Integer, ForeignKey("course.id"))

    course = relationship("Course", back_populates="course_groups")
    requests = relationship("Request", back_populates="course_group")
    course_group_timetables = relationship("CourseGroupTimetable", back_populates="course_group")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"free_places='{self.free_places}', "
            f"course='{self.course}')>"
        )


class CourseGroupTimetable(Base, BaseMixin):
    __tablename__ = "course_group_timetable"

    course_group_id = Column(Integer, ForeignKey("course_group.id"))
    time = Column(TIME())
    weekday = Column(Enum(WeekDaysEnum))

    course_group = relationship("CourseGroup", back_populates="course_group_timetables")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"course_group_id='{self.course_group_id}', "
            f"time='{self.time}', "
            f"weekday='{self.weekday}',"
            f"course_group='{self.course_group}')>"
        )


class Request(Base):
    __tablename__ = "request"

    __table_args__ = (
        PrimaryKeyConstraint('course_group_id', 'children_id'),
    )
    course_group_id = Column(Integer, ForeignKey("course_group.id"))
    children_id = Column(BigInteger, ForeignKey("children.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.no_payment)

    course_group = relationship("CourseGroup", back_populates="requests")
    children = relationship("Children", back_populates="requests")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"course_group={self.course_group}, "
            f"children='{self.children}', "
            f"payment_status='{self.payment_status}')>"
        )
