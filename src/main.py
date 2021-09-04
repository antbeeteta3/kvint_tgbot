#!/usr/bin/env python3

# https://github.com/pytransitions/transitions


import argparse
import logging

import transport
import dialog


class PizzaShop:

	def init_args(self, arg_src = None):
		parser = argparse.ArgumentParser()

		parser.add_argument('--transport', default='telegram', help='Transport type')
		parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

		return parser.parse_args(arg_src)

	def init_logger(self, level, root_level):
		logging.basicConfig(format='[%(asctime)s.%(msecs)d][%(levelname)s] %(message)s',
				datefmt='%d %b %H:%M:%S')

		log = logging.getLogger(self.__class__.__name__)

		log.setLevel(level)
		logging.getLogger().setLevel(root_level)

		return log

	def __init__(self):
		self.args = self.init_args()
		self.log = self.init_logger(logging.DEBUG if self.args.verbose else logging.INFO, logging.DEBUG if self.args.verbose else logging.WARNING)

		self.dialogs = {}		# user_id : Dialog

		self.transport = transport.create_transport(self.args.transport, self.on_recv_message)

	def on_recv_message(self, text, user_id, user_name, **context):
		dlg = self.dialogs.get(user_id)
		if not dlg:
			dlg = self.dialogs.setdefault(user_id, dialog.PizzaDialog(user_name))
			self.log.info(f'started new dialog: {user_id}')

		reply = dlg.process_message(text)

		self.log.debug(f'{user_id}: "{text}" -> Me: "{reply}"')
		if reply:
			self.transport.send_reply(reply, **context)

		if dlg.is_finished():
			self.dialogs.pop(user_id)
			self.log.info(f'finished dialog: {user_id}')

	def main(self):
		self.transport.run()


if __name__ == '__main__':
	PizzaShop().main()
