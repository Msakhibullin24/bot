import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType

import config
from app.handlers.add_children import register_handlers_add_children
from app.handlers.children_list import register_handlers_children_list
from app.handlers.common import register_handlers_common
from app.handlers.parent import register_handlers_parent
from app.handlers.registration import register_handlers_registration
from app.handlers.edit_parent import register_handlers_edit_parent
from handlers.course_list import register_handlers_course_list
from handlers.edit_children import register_handlers_edit_children
from handlers.master_class_list import register_handlers_master_class_list
from handlers.request_list import register_handlers_request_list

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

PRICE = types.LabeledPrice(label="мастер класс", amount=500*100)  # в копейках (руб)


@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Покупка",
                           description="мастер класс",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


async def main():
    register_handlers_common(dp)
    register_handlers_registration(dp)
    register_handlers_parent(dp)
    register_handlers_edit_parent(dp)
    register_handlers_add_children(dp)
    register_handlers_children_list(dp)
    register_handlers_edit_children(dp)
    register_handlers_course_list(dp)
    register_handlers_master_class_list(dp)
    register_handlers_request_list(dp)

    await dp.skip_updates()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
