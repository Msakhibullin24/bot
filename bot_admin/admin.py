from django.contrib import admin
from .models import Parent, Children, Course, CourseGroup, CourseGroupTimetable, Request


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'name', 'surname', 'patronymic', 'phone_number']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    search_fields = ('name', 'surname', 'patronymic')
    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)


@admin.register(Children)
class ChildrenAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'name', 'surname', 'patronymic', 'date_of_birth', 'parent']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    search_fields = ('name', 'surname', 'patronymic')
    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'name', 'price', 'duration', 'age']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    search_fields = ('name',)
    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'name', 'free_places', 'course']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    search_fields = ('name',)
    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)


@admin.register(CourseGroupTimetable)
class CourseGroupTimetableAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'updated_at', 'course_group', 'time', 'weekday']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['course_group', 'children', 'created_at', 'updated_at', 'payment_status']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    list_filter = ('updated_at',)

    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)
