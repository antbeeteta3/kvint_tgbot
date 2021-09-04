#!/usr/bin/env python3


import abc
import os

from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters


# ---- Интерфейс ----

class BaseTransport(abc.ABC):

	def __init__(self, on_recv_message):
		self.on_recv_message = on_recv_message

	# для вызова наследниками, context - для передачи в send_reply
	def _report_recv_message(self, text, user_id, user_name, **context):
		self.on_recv_message(text, user_id, user_name, **context)

	@abc.abstractmethod
	def send_reply(self, text, **context):
		pass

	@abc.abstractmethod
	def run(self):
		pass


# ---- Реализация ----

class TelegramBotTransport(BaseTransport):

	def __init__(self, on_recv_message):
		BaseTransport.__init__(self, on_recv_message)

		token_env_name = 'TGBOT_TOKEN'
		token = os.environ.get(token_env_name)
		if not token:
			raise RuntimeError(f'Set environment variable {token_env_name}')

		self.updater = Updater(token=token, use_context=True)

		self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self._any_message_handler))

	def _any_message_handler(self, update, context):
		# будем игнорировать отредактированное, для красоты диалога
		if update.edited_message is update.effective_message:
			return

		self._report_recv_message(update.effective_message.text,
									update.effective_chat.id,
									update.effective_chat.first_name,
									update=update, context=context)

	def send_reply(self, text, *, update, context):
		context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	def run(self):
		self.updater.start_polling()


# ---- "Фабрика"

def create_transport(name, on_recv_message):
	if name == 'telegram':
		return TelegramBotTransport(on_recv_message)

	raise NotImplementedError(f'transport {name} is not implemented yet')



# ---- dev test

if __name__ == '__main__':

	class RespectfulStupidInterlocutor(TelegramBotTransport):
		def __init__(self):
			self.transport = create_transport('telegram', self.on_recv_message)

		def on_recv_message(self, text, user_id, user_name, **context):
			reply = f'Dear {user_name}, your words\n"{text}"\nare very wise.\nI will remember these!'
			self.transport.send_reply(reply, **context)

			#self.transport.send_reply('Write again!', **context)

	RespectfulStupidInterlocutor().transport.run()
