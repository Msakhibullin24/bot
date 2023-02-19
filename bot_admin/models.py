from django.db import models


class WeekDaysEnum(models.TextChoices):
    monday = 'monday', 'Понедельник'
    tuesday = 'tuesday', 'Вторник'
    wednesday = 'wednesday', 'Среда'
    thursday = 'thursday', 'Четверг'
    friday = 'friday', 'Пятница'
    saturday = 'saturday', 'Суббота'
    sunday = 'sunday', 'Воскресенье'


class PaymentStatusEnum(models.TextChoices):
    checked = 'checked', 'оплата проверена'
    no_checked = 'no_checked', 'оплата не проверена'
    no_payment = 'no_payment', 'не оплачено'


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='Дата изменения')

    class Meta:
        abstract = True


class Children(BaseModel):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Имя')
    surname = models.CharField(max_length=50, blank=True, null=True, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name='Отчество')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    parent = models.ForeignKey('Parent', models.DO_NOTHING, blank=True, null=True, verbose_name='Родитель')

    def __str__(self):
        return f"Ребенок {self.id} {self.surname} {self.name} {self.patronymic}, {self.date_of_birth}"

    class Meta:
        managed = False
        db_table = 'children'
        verbose_name = 'Ребенок'
        verbose_name_plural = 'Дети'


class Course(BaseModel):
    name = models.CharField(unique=True, max_length=150, blank=True, null=True, verbose_name='Название')
    price = models.IntegerField(blank=True, null=True, verbose_name='Цена в месяц')
    duration = models.IntegerField(blank=True, null=True, verbose_name='Продолжительность занятия, в минутах')
    age = models.IntegerField(blank=True, null=True, verbose_name='Минимальный возраст')

    def __str__(self):
        return f"Курс {self.id}, {self.name}, {self.price} р. в месяц, {self.duration} минут, {self.age}+"

    class Meta:
        managed = False
        db_table = 'course'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class CourseGroup(BaseModel):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Название')
    free_places = models.IntegerField(blank=True, null=True, verbose_name='Количество свободных мест')
    course = models.ForeignKey(Course, models.DO_NOTHING, blank=True, null=True, verbose_name='Курс', related_name='course_groups')

    def __str__(self):
        return f"Группа {self.id}, {self.name}, {self.free_places} свободных мест, {self.course.name}"

    class Meta:
        managed = False
        db_table = 'course_group'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class CourseGroupTimetable(BaseModel):
    course_group = models.ForeignKey(CourseGroup, models.DO_NOTHING, blank=True, null=True, verbose_name='Группа')
    time = models.TimeField(blank=True, null=True, verbose_name='Время')
    weekday = models.TextField(blank=True, null=True, choices=WeekDaysEnum.choices, verbose_name='День недели')

    def __str__(self):
        return f"Расписание группы {self.id}, {self.time}, {self.weekday}, {self.course_group}"

    class Meta:
        managed = False
        db_table = 'course_group_timetable'
        verbose_name = 'Расписание группы'
        verbose_name_plural = 'Расписания группы'


class Parent(BaseModel):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Имя')
    surname = models.CharField(max_length=50, blank=True, null=True, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name='Отчество')
    phone_number = models.CharField(unique=True, max_length=20, blank=True, null=True, verbose_name='Номер телефона')

    def __str__(self):
        return f"Родитель {self.id} {self.surname} {self.name} {self.patronymic}, {self.phone_number}"

    class Meta:
        managed = False
        db_table = 'parent'
        verbose_name = 'Родитель'
        verbose_name_plural = 'Родители'


class Request(models.Model):
    course_group = models.OneToOneField(CourseGroup, models.DO_NOTHING, primary_key=True, verbose_name='Группа')
    children = models.ForeignKey(Children, models.DO_NOTHING, verbose_name='Ребенок')
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='Дата изменения')
    payment_status = models.TextField(
        blank=True, null=True, choices=PaymentStatusEnum.choices,
        verbose_name='Статус оплаты', default=PaymentStatusEnum.no_payment)

    def __str__(self):
        return f"Заявка ребенок:{self.children}, группа: {self.course_group}, статус: {self.payment_status}"

    class Meta:
        managed = False
        db_table = 'request'
        unique_together = (('course_group', 'children'),)
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
