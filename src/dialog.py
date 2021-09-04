#!/usr/bin/env python3


from transitions import Machine


class PizzaDialog:

	def __init__(self, user_name):
		self.user_name = user_name

		self.reply = self.size = self.payment = self.done = None

		# и собственно стейт машина
		states = ['start', 'wait_size', 'wait_payment', 'wait_confirmation', 'end']

		self.machine = Machine(model=self, states=states, initial='start')

		self.machine.add_ordered_transitions(loop=False,
						conditions=[lambda *a: True, 'cnd_from_size', 'cnd_from_payment', 'cnd_from_wait_confirmation'])

		self.machine.add_transition(trigger='try_again', source='end', dest='wait_size')


	def on_exit_start(self, _):
		self.reply += f'Здравствуйте, {self.user_name}!\n'

	def on_enter_wait_size(self, _):
		self.reply += 'Какую вы хотите пиццу? Большую или маленькую? '

	def cnd_from_size(self, text):
		text = text.lower()
		if text in ('большую', 'маленькую'):
			self.size = text
			return True
		self.reply += 'Простите, не понял, так большую или маленькую? '

	def on_enter_wait_payment(self, _):
		self.reply += 'Как вы будете платить? Картой или наличкой? '

	def cnd_from_payment(self, text):
		text = text.lower()
		if text in ('картой', 'наличкой'):
			self.payment = text
			return True
		self.reply += 'Простите, не понял, так картой или наличкой? '

	def on_enter_wait_confirmation(self, _):
		self.reply += f'Итак, вы хотите {self.size} пиццу, оплата - {self.payment}. Правильно? '

	def cnd_from_wait_confirmation(self, text):
		text = text.lower()
		if text in ('да', 'нет'):
			if text == 'да':
				self.done = True
			return True
		self.reply += 'Простите, не понял, да или нет? '

	def on_enter_end(self, _):
		if self.done:
			self.reply += f'Спасибо за заказ! '
		else:
			self.reply += f'Ок, попробуем разобраться заново. '
			self.try_again('')

	# -----

	def is_finished(self):
		return self.done


	def process_message(self, text):
		self.reply = ''

		self.next_state(text)

		return self.reply


# ---- dev test

if __name__ == '__main__':

	dlg = PizzaDialog('Вася')

	def replic(msg, in_=True):
		if in_:
			print(msg)
		print(dlg.process_message(msg))
		print

	while 1:
		replic(input(), False)
		if dlg.is_finished():
			break
