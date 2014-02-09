from .base import FunctionalTest
from unittest import skip


class ItemValidationTest(FunctionalTest):


	def test_cannot_insert_empty_list_items(self):
		# Edith goes to the home page and accidently tries to submit
		# an empty list item. She hits enter on the empty input box
		self.browser.get(self.server_url)
		self.get_item_input_box().send_keys('\n')

		# The homepage refreshes and there is an error saying that
		# list items cannot be blank
		error = self.get_error_element()
		self.assertEqual(error.text, "You can't have an empty list item")

		# She tries again, this time entering some text before submitting.
		# This time it works
		self.get_item_input_box().send_keys('Buy milk\n')
		self.check_for_row_in_list_table('1: Buy milk')

		# Perversly, she tries submitting another empty list item
		self.get_item_input_box().send_keys('\n')

		# She receives a similar warning on the list page
		self.check_for_row_in_list_table('1: Buy milk')
		error = self.get_error_element()
		self.assertEqual(error.text, "You can't have an empty list item")

		# And she can correct it by entering some text.
		self.get_item_input_box().send_keys('Make tea\n')
		self.check_for_row_in_list_table('1: Buy milk')
		self.check_for_row_in_list_table('2: Make tea')


	def test_cannot_add_duplicate_items(self):
		# Edit goes to the home page and starts a new list
		self.browser.get(self.server_url)
		self.get_item_input_box().send_keys('Buy wellies\n')
		self.check_for_row_in_list_table('1: Buy wellies')

		# She accidentally tries to enter a duplicate item
		self.get_item_input_box().send_keys('Buy wellies\n')

		# She sees a helpful error message
		self.check_for_row_in_list_table('1: Buy wellies')
		error = self.get_error_element()
		self.assertEqual(error.text, "You've already got this in your list")


	def test_error_messages_are_cleared_on_input(self):
		# Edith starts a new list in a way that causes a validation error:
		self.browser.get(self.server_url)
		self.get_item_input_box().send_keys('\n')
		error = self.get_error_element()
		self.assertTrue(error.is_displayed())

		# She starts typing in the  input box to clear the error
		self.get_item_input_box().send_keys('a')

		# She is pleased to see that the error message disappears
		error = self.get_error_element()

	def get_error_element(self):
		return self.browser.find_element_by_css_selector('.has-error')


