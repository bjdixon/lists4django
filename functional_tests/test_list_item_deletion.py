from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session
from lists.models import Item


class DeleteListItems(FunctionalTest):

	def test_user_can_delete_list_items(self):
		# User (Edith) visits homepage and logs in
		self.create_pre_authenticated_session('edith@mockymyid.com')
		self.browser.get(self.server_url)	
		# she is invited to enter a to-do item straight away
		inputbox = self.get_item_input_box()

		# she types "Buy peacock feathers" into a text box
		inputbox.send_keys('Buy peacock feathers')

		# when she hits enter she is take to a new URL,
		# and now the page lists,
		# "1: Buy peacock feathers" as an item in a to-do list table
		inputbox.send_keys(Keys.ENTER)
		edith_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')
		self.check_for_row_in_list_table('1: Buy peacock feathers')

		# she also sees that the list item is clickable
		delete_button = self.browser.find_element_by_link_text('1: Buy peacock feathers')

		# wanting to test out the button she clicks it
		delete_button.click()

		# the page refreshes and the item is no longer there
		self.assertNotIn('1: Buy peacock feathers', self.browser.find_element_by_tag_name('body').text)

		# Edith decides to add an item as an empty list looks weird
		inputbox = self.get_item_input_box()
		inputbox.send_keys('Buy some other feathers?')
		inputbox.send_keys(Keys.ENTER)

		# Satisfied knowing her list isn't empty she goes to bed
		self.assertIn('Buy some other feathers?', self.browser.find_element_by_tag_name('body').text)
		self.browser.quit()

		# Edith's evil twin sister and nemesis Carly sneaks out of the shadows. She's been
		# watching the whole time and noticed the url when Edith hovered over the delete button. 
		item_id = Item.objects.get(text='Buy some other feathers?').id
		self.assertNotEqual(item_id, None)
		self.assertEqual(Item.objects.count(), 1)

		# She decides to visit the delete url to see if she can delete Ediths latest list item
		self.browser = webdriver.Firefox()
		self.browser.get(self.server_url + '/lists/delete/item/%d/' % (item_id,))
		
		# unfortunately for Carly she recieves an error message
		self.assertIn('Not Found', self.browser.find_element_by_tag_name('body').text)

		# and the item still exists
		self.assertEqual(Item.objects.count(), 1)
		self.assertEqual('Buy some other feathers?', Item.objects.first().text)

