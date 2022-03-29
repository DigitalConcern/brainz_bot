import telebot
import os

bot = telebot.TeleBot("5229104005:AAG8gMJJ86I34BBsdkk3sBHf8fB8oVxhIzM")

from web import services


@bot.message_handler(commands=["test"])
def start(message):
    bot.send_message(message.from_user.id, "Bot hears you!")


@bot.message_handler(commands=["start"])
def start(message):
    user, is_created = services.add_user(
        tg_id=message.from_user.id,
        username=message.from_user.username
    )
    if is_created:
        bot.send_message(message.from_user.id, "You have successfully registered in the bot!")
    else:
        bot.send_message(message.from_user.id, "You are already registered in the bot!")


@bot.message_handler(commands=["id"])
def send_my_id(message):
    bot.send_message(message.from_user.id,
                     f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>",
                     parse_mode="HTML")
