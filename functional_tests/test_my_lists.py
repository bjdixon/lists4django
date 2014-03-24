from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
User = get_user_model()
from django.contrib.sessions.backends.db import SessionStore

from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session


class MyListsTest(FunctionalTest):

	def test_logged_in_users_lists_are_saved_as_my_lists(self):
		# edith is a logged-in user
		email = 'edith@mockmyid.com'
		self.create_pre_authenticated_session(email)

		# she goes to the home page and starts a list
		self.browser.get(self.server_url)
		self.get_item_input_box().send_keys('Reticulate splines\n')
		self.get_item_input_box().send_keys('Immanentize eschaton\n')
		first_list_url = self.browser.current_url

		#she notices a "My lists" link for the first time.
		self.browser.find_element_by_link_text('My lists').click()

		# she sees that her list is in there, named according to it's 
		# first list item
		self.browser.find_element_by_link_text('Reticulate splines').click()
		self.assertEqual(self.browser.current_url, first_list_url)

		# she decides to start another list, just to see
		self.browser.get(self.server_url)
		self.get_item_input_box().send_keys('Click cows\n')
		second_list_url = self.browser.current_url

		# under "My lists", her new list appears
		self.browser.find_element_by_link_text('My lists').click()
		self.browser.find_element_by_link_text('Click cows').click()
		self.assertEqual(self.browser.current_url, second_list_url)

		# she logs out. The "My lists" option disappears
		self.browser.find_element_by_id('id_logout').click()
		self.assertEqual(
			self.browser.find_elements_by_link_text('My lists'),
			[]
		)


	def create_pre_authenticated_session(self, email):
		if self.against_staging:
			session_key = create_session_on_server(self.server_host, email)
		else:
			session_key = create_pre_authenticated_session(email)
		## to get a cookie we need to visit the domain
		## 404 pages load the quickest
		self.browser.get(self.server_url + "/404_no_such_url/")
		self.browser.add_cookie(dict(
			name=settings.SESSION_COOKIE_NAME,
			value=session_key,
			path='/',
		))

