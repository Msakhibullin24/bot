import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType

from db import Parent, Session

# log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# prices
PRICE = types.LabeledPrice(label="мастер класс", amount=500*100)  # в копейках (руб)


# buy
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


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Send your surname, name and patronymic in this order")


@dp.message_handler()
async def echo(message: types.Message):
    try:
        surname, name, patronymic = message.text.split(' ')
        chat_id = message.chat.id
        with Session() as session:
            parent = Parent(id=chat_id, name=name, surname=surname, patronymic=patronymic)
            session.add(parent)
            session.commit()
            await message.answer(f'created parent: {parent}')
    except ValueError:
        await message.answer('surname, name and patronymic not correct')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
