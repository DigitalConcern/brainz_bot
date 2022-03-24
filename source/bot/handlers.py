# import telebot
# from ..web import services
# from ..objects import MyBot
#
# def start(message):
#     user, is_created = services.add_user(
#         tg_id=message.from_user.id,
#         name=message.from_user.username
#     )
#
#     if is_created:
#         message.answer("You have successfully registered in the bot!")
#     else:
#         message.answer("You are already registered in the bot!")
#
#
# def send_my_id(message):
#     await message.answer(
#         f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>"
#     )
# MyBot.bot.register_message_handlers(start, commands=["start"])
# MyBot.bot.register_message_handlers(send_my_id, commands=["id"])