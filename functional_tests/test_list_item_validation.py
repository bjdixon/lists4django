from .base import FunctionalTest
from unittest import skip


class ItemValidationTest(FunctionalTest):


	def test_cannot_insert_empty_list_items(self):
		# Edith goes to the home page and accidently tries to submit
		# an empty list item. She hits enter on the empty input box

		# The homepage refreshes and there is an error saying that
		# list items cannot be blank

		# She tries again, this time entering some text before submitting.
		# This time it works

		# Perversly, she tries submitting another empty list item

		# She receives a similar warning on the list page

		# And she can correct it by entering some text.
		self.fail('write me')



