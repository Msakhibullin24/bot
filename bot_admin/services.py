import requests
from django.conf import settings


def send_message(parent_id, text):
    data = {
        "chat_id": parent_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    response = requests.post(
        f"{settings.TELEGRAM_URL}{settings.TOKEN}/sendMessage", data=data
    )

    return response


def send_success_payment(obj):
    message_text = f'Успешная оплата\n' \
                   f'{obj.course_group.course.name}'
    parent_id = obj.children.parent.id
    return send_message(parent_id, message_text)


def send_error_payment(obj):
    message_text = f'Ошибка в оплате\n' \
                   f'{obj.course_group.course.name}'
    parent_id = obj.children.parent.id
    return send_message(parent_id, message_text)
