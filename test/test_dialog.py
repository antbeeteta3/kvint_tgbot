#!/usr/bin/env python3


import unittest
from transitions import MachineError


import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import dialog



class PizzaDialogTest(unittest.TestCase):

	def setUp(self):
		self.dlg = dialog.PizzaDialog('Петя')
		self.assertEqual(self.dlg.state, 'start')


	def check_message(self, msg, expected_state):
		self.dlg.process_message(msg)
		self.assertEqual(self.dlg.state, expected_state)

		if self.dlg.state != 'end':
			self.assertFalse(self.dlg.is_finished())


	def test_base_scenario(self):
		self.check_message('hi', 'wait_size')
		self.check_message('большую', 'wait_payment')
		self.check_message('наличкой', 'wait_confirmation')
		self.check_message('да', 'end')

		self.assertTrue(self.dlg.is_finished())


	def test_unideal_scenario(self):
		self.check_message('??', 'wait_size')
		self.check_message('??', 'wait_size')
		self.check_message('??', 'wait_size')
		self.check_message('большую', 'wait_payment')
		self.check_message('--', 'wait_payment')
		self.check_message('--', 'wait_payment')
		self.check_message('наличкой', 'wait_confirmation')
		self.check_message('', 'wait_confirmation')
		self.check_message('', 'wait_confirmation')
		self.check_message('нет', 'wait_size')

		self.assertFalse(self.dlg.is_finished())

		self.check_message('!!', 'wait_size')
		self.check_message('---', 'wait_size')
		self.check_message('??', 'wait_size')
		self.check_message('большую', 'wait_payment')
		self.check_message('00', 'wait_payment')
		self.check_message('11', 'wait_payment')
		self.check_message('наличкой', 'wait_confirmation')
		self.check_message('', 'wait_confirmation')
		self.check_message('', 'wait_confirmation')
		self.check_message('да', 'end')

		self.assertTrue(self.dlg.is_finished())


	def test_wrong_usage_scenario(self):
		self.test_base_scenario()

		self.assertRaises(MachineError, self.dlg.process_message, 'any message')



if __name__ == '__main__':
	unittest.main()
