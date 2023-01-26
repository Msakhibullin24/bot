import psycopg2
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler

from db import Session, Parent


def start(bot, update):
    update.message.reply_text('Ваше ФИО')
    return 'FULL_NAME'


def full_name(bot, update):
    full_name = update.message.text
    update.message.reply_text('Номер?')
    return 'PHONE_NUMBER'


def phone_number(bot, update):
    phone_number = update.message.text
    chat_id = update.message.chat_id

    # conn = psycopg2.connect(dbname="yourdbname", user="yourusername", password="yourpassword", host="yourhost")
    # cur = conn.cursor()
    # cur.execute("INSERT INTO users (username, full_name, phone_number) VALUES (%s, %s, %s)",
    #             (username, full_name, phone_number))
    # conn.commit()
    # cur.close()
    # conn.close()

    with Session() as session:
        parent = Parent(id=chat_id, name=full_name, phone_number=phone_number)
        session.add(parent)
        session.commit()

    update.message.reply_text(f'Thanks, we have added your phone number {phone_number}')
    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('пока')
