from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Parent, Children, Course, CourseGroup, CourseGroupTimetable, Request, RequestFile, PaymentStatusEnum
from .services import send_success_payment, send_error_payment


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


class ChildInline(admin.TabularInline):
    can_delete = False
    model = RequestFile
    extra = 0
    fields = ['file']

    @admin.display(description='svbf')
    def view_all(self, obj):
        return '123'

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    inlines = [ChildInline]

    list_display = ['id', 'course_group', 'children', 'created_at', 'updated_at', 'payment_status']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at',]

    list_filter = ('updated_at',)
    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)

    def save_model(self, request, obj, form, change):
        if change:
            if 'payment_status' in form.changed_data:
                if obj.payment_status == PaymentStatusEnum.success.value:
                    send_success_payment(obj)

                elif obj.payment_status == PaymentStatusEnum.error.value:
                    send_error_payment(obj)
        return super(RequestAdmin, self).save_model(request, obj, form, change)


@admin.register(RequestFile)
class RequestFileAdmin(admin.ModelAdmin):
    list_select_related = ('request',)
    list_display = ['id', 'request', 'created_at', 'updated_at', 'blank_link_to_file']
    list_display_links = list_display

    readonly_fields = ['created_at', 'updated_at']

    list_filter = ('updated_at',)
    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)

    @admin.display(description='Файл')
    def blank_link_to_file(self, obj):
        if obj.file:
            return format_html(
                f'<a  href="{settings.MEDIA_URL + str(obj.file)}" class="button" target="_blank">Файл</a>&nbsp;',
            )
        else:
            return ''
