from mock import patch, Mock
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()
from django.test import TestCase

from accounts.authentication import(
	PERSONA_VERIFY_URL, PersonaAuthenticationBackend, User,
)

@patch('accounts.authentication.requests.post')
class AuthenticateTest(TestCase):

	def setUp(self):
		self.backend = PersonaAuthenticationBackend()

	def test_sends_assertion_to_mozilla_with_domain(self, mock_post):
		self.backend.authenticate('an assertion')
		mock_post.assert_called_once_with(
			PERSONA_VERIFY_URL,
			data={'assertion': 'an assertion', 'audience': settings.DOMAIN}
		)

	def test_returns_none_if_response_errors(self, mock_post):
		mock_post.return_value.ok = False
		mock_post.return_value.json.return_value = {}
		user = self.backend.authenticate('an assertion')
		self.assertIsNone(user)

	def test_returns_none_if_status_not_okay(self, mock_post):
		mock_post.return_value.json.return_value = {'status': 'not okay!'}
		user = self.backend.authenticate('an assertion')
		self.assertIsNone(user)

	def test_finds_existing_user_with_email(self, mock_post):
		mock_post.return_value.json.return_value = {'status': 'okay', 'email': 'a@b.com'}
		User.objects.create(email='someone@else.com')
		actual_user = User.objects.create(email='a@b.com')
		found_user = self.backend.authenticate('an assertion')
		self.assertEqual(found_user, actual_user)

	def test_creates_new_user_if_necessary_for_valid_assertion(self, mock_post):
		mock_post.return_value.json.return_value = {'status': 'okay', 'email': 'a@b.com'}
		found_user = self.backend.authenticate('an assertion')
		new_user = User.objects.all()[0]
		self.assertEqual(found_user, new_user)
		self.assertEqual(found_user.email, 'a@b.com')

class GetUserTest(TestCase):

	@patch('accounts.authentication.User.objects.get')
	def test_gets_user_from_ORM_using_email(self, mock_User_get):
		backend = PersonaAuthenticationBackend()
		found_user = backend.get_user('a@b.com')
		self.assertEqual(found_user, mock_User_get.return_value)
		mock_User_get.assert_called_once_with(email='a@b.com')

	@patch('accounts.authentication.User.objects.get')
	def test_returns_none_if_user_does_not_exist(self, mock_User_get):
		def raise_no_user_error(*_, **__):
			raise User.DoesNotExist()
		mock_User_get.side_effect = raise_no_user_error
		backend = PersonaAuthenticationBackend()

		self.assertIsNone(backend.get_user('a@b.com'))

