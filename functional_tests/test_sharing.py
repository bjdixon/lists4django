from selenium import webdriver
from .base import FunctionalTest
from .home_and_list_pages import HomePage

def quit_if_possible(browser):
	try: browser.quit()
	except: pass


class SharingTest(FunctionalTest):
	
	def test_logged_in_users_lists_are_saved_as_my_lists(self):
		# edith is a logged in user
		self.create_pre_authenticated_session('edith@email.com')
		edith_browser = self.browser
		self.addCleanup(lambda: quit_if_possible(edith_browser))

		# her friend oni is also hanging out on the lists site
		oni_browser = webdriver.Firefox()
		self.addCleanup(lambda: quit_if_possible(oni_browser))
		self.browser = oni_browser
		self.create_pre_authenticated_session('oni@email.com')

		# edith goes to the home page and starts a list
		self.browser = edith_browser
		list_page = HomePage(self).start_new_list('Get help')

		# she notices a "Share this list" option
		share_box = list_page.get_share_box()
		self.assertEqual(
			share_box.get_attribute('placeholder'),
			'your@friends-email.com'
		)

		# she shares her list.
		# the page updates to say that its been shared with oni
		list_page.share_list_with('oni@email.com')

		# oni now goes to the lists page with his browser
		self.browser = oni_browser
		HomePage(self).go_to_home_page().go_to_my_lists_page()

		# he sees ediths list in there
		self.browser.find_element_by_link_text('Get help').click()

		# on the list page, oni can see that it's ediths list
		self.wait_for(lambda: self.assertEqual(
			list_page.get_list_owner(),
			'edith@email.com'
		))

		# he adds an item to the list
		list_page.add_new_item('Hi Edith!')

		# when edith refreshes the page, she sees oni's addition
		self.browser = edith_browser
		self.broswer.refresh()
		list_page.wait_for_new_item_in_list('Hi Edith!', 2)

