import sys
from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.support.ui import WebDriverWait
from django.conf import settings
from .server_tools import create_session_on_server, reset_database
from .management.commands.create_session import create_pre_authenticated_session

class FunctionalTest(LiveServerTestCase):

	
	@classmethod
	def setUpClass(cls):
		for arg in sys.argv:
			if 'liveserver' in arg:
				cls.server_host = arg.split('=')[1]
				cls.server_url = 'http://' + cls.server_host
				cls.against_staging = True
				return
		LiveServerTestCase.setUpClass()
		cls.against_staging = False
		cls.server_url = cls.live_server_url


	@classmethod
	def tearDownClass(cls):
		if not cls.against_staging:
			LiveServerTestCase.tearDownClass()


	def setUp(self):
		if self.against_staging:
			reset_database(self.server_host)
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)


	def tearDown(self):
		self.browser.quit()


	def check_for_row_in_list_table(self, row_text):
		table = self.browser.find_element_by_id('id_list_table')
		rows = table.find_elements_by_tag_name('tr')
		self.assertIn(row_text, [row.text for row in rows])


	def get_item_input_box(self):
		return self.browser.find_element_by_id('id_text')

	
	def wait_for_element_with_id(self, element_id):
		WebDriverWait(self.browser, 30).until(
			lambda b: b.find_element_by_id(element_id)
		)

	def wait_to_be_logged_in(self, email):
		self.wait_for_element_with_id('id_logout')
		navbar = self.browser.find_element_by_css_selector('.navbar')
		self.assertIn(email, navbar.text)

	def wait_to_be_logged_out(self, email):
		self.wait_for_element_with_id('id_login')
		navbar = self.browser.find_element_by_css_selector('.navbar')
		self.assertNotIn(email, navbar.text)

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

