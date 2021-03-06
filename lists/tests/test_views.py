from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user_model
User = get_user_model()
from lists.views import home_page, new_list, delete_item
from django.http import HttpRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from unittest import skip
from lists.models import Item, List
from django.utils.html import escape
from lists.forms import (ItemForm, EMPTY_LIST_ERROR, DUPLICATE_ITEM_ERROR, ExistingListItemForm,)


class HomePageTest(TestCase): 


	maxDiff = None

	def test_root_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	@skip
	def test_home_page_returns_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		expected_html = render_to_string('home.html', {'form': ItemForm()})
		self.assertMultiLineEqual(response.content.decode(), expected_html)
	
	def test_home_page_renders_home_template(self):
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

	def test_home_page_uses_item_form(self):
		response = self.client.get('/')
		self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):


	def test_uses_list_template(self):
		list_ = List.objects.create()
		response = self.client.get('/lists/%d/' % (list_.id,))
		self.assertTemplateUsed(response, 'list.html')

	def test_displays_only_items_for_that_list(self):
		correct_list = List.objects.create()
		Item.objects.create(text='itemy 1', list=correct_list)
		Item.objects.create(text='itemy 2', list=correct_list)
		other_list = List.objects.create()
		Item.objects.create(text='other list item 1', list=other_list)
		Item.objects.create(text='other list item 2', list=other_list)

		response = self.client.get('/lists/%d/' % (correct_list.id,))

		self.assertContains(response, 'itemy 1')
		self.assertContains(response, 'itemy 2')
		self.assertNotContains(response, 'other list item 1')
		self.assertNotContains(response, 'other list item 2')

	def test_passes_correct_list_to_template(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()
		response = self.client.get('/lists/%d/' % (correct_list.id,))
		self.assertEqual(response.context['list'], correct_list)

	def test_can_save_a_POST_request_to_an_existing_list(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()

		self.client.post(
			'/lists/%d/' % (correct_list.id,),
			data={'text': 'A new item for an existing list'}
		)

		self.assertEqual(Item.objects.all().count(), 1)
		new_item = Item.objects.all()[0]
		self.assertEqual(new_item.text, 'A new item for an existing list')
		self.assertEqual(new_item.list, correct_list)

	def test_POST_redirects_to_list_view(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()
		response = self.client.post(
			'/lists/%d/' % (correct_list.id,),
			data = {'text': 'A new item for an existing list'}
		)
		self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))

	def test_validation_errors_end_up_on_lists_page(self):
		listey = List.objects.create()

		response = self.client.post(
			'/lists/%d/' % (listey.id,),
			data = {'text': ''}
		)
		self.assertEqual(Item.objects.all().count(), 0)
		self.assertTemplateUsed(response, 'list.html')
		expected_error = escape("You can't have an empty list item")
		self.assertContains(response, expected_error)

	def test_displays_item_form(self):
		list_ = List.objects.create()
		response = self.client.get('/lists/%d/' % (list_.id,))
		self.assertIsInstance(response.context['form'], ExistingListItemForm)
		self.assertContains(response, 'name="text"')


class NewListTest(TestCase):


	def test_saving_a_POST_request(self):
		self.client.post(
			'/lists/new',
			data={'text': 'A new list item'}
		)
		self.assertEqual(Item.objects.all().count(), 1)
		new_item = Item.objects.all()[0]
		self.assertEqual(new_item.text, 'A new list item')

	def test_redirects_after_POST(self): 
		response = self.client.post(
			'/lists/new',
			data={'text': 'A new list item'}
		)
		new_list = List.objects.all()[0]
		self.assertRedirects(response, '/lists/%d/' % (new_list.id,))

	def post_invalid_input(self):
		list_ = List.objects.create()
		return self.client.post(
			'/lists/%d/' % (list_.id,),
			data={'text': ''}
		)

	def test_invalid_input_means_nothing_saved_to_db(self):
		self.post_invalid_input()
		self.assertEqual(Item.objects.all().count(), 0)

	def test_invalid_input_renders_list_template(self):
		response = self.post_invalid_input()
		self.assertTemplateUsed(response, 'list.html')

	def test_list_items_can_be_deleted(self):
		request = HttpRequest()
		request.user = User.objects.create(email='user@email.com')
		request.POST['text'] = 'delete me'
		new_list(request)
		self.assertEqual(Item.objects.count(), 1)
		request.POST['id'] = Item.objects.first().id
		delete_item(request, item_id=Item.objects.first().id)
		self.assertEqual(Item.objects.count(), 0)

	def test_correct_item_is_deleted(self):
		request = HttpRequest()
		request.user = User.objects.create(email='user@email.com')
		list_ = List.objects.create(owner=request.user)
		first_item = Item.objects.create(list=list_, text='Keep me')
		second_item = Item.objects.create(list=list_, text='Delete me')
		self.assertEqual(Item.objects.count(), 2)
		request.POST['id'] = second_item.id
		delete_item(request, item_id=second_item.id)
		self.assertEqual(Item.objects.count(), 1)
		remaining_item = Item.objects.first()
		self.assertEqual('Keep me', remaining_item.text)

	def test_no_delete_buttons_when_not_logged_in(self):
		request = HttpRequest()
		list_ = List.objects.create()
		list_.owner = User.objects.create(email='owner@email.com')
		no_delete_item = Item.objects.create(list=list_, text='no delete')
		request.user = None
		self.assertNotEqual(list_.owner, request.user)
		response = self.client.post('/lists/%d/' % (list_.id,))
		self.assertNotContains(response, '/lists/delete/item/%d' % (no_delete_item.id,))


	def test_attempted_deletes_that_arent_allowed_are_redirected_to_403_error(self):
		request = HttpRequest()
		list_ = List.objects.create()
		list_.owner = User.objects.create(email='owner@email.com')
		no_delete_item = Item.objects.create(list=list_, text='no delete')
		request.user = User.objects.create(email='not-owner@email.com')
		response = self.client.post('/lists/delete/item/%d/' % (no_delete_item.id,))
		self.assertEqual(response.status_code, 403)

	def test_403_error_uses_correct_template(self):
		response = self.client.post('/lists/error/403/')
		self.assertTemplateUsed(response, 'error_403.html')

	def test_only_owner_can_delete_their_list_items(self):
		request = HttpRequest()
		list_ = List.objects.create()
		list_.owner = User.objects.create(email='owner@email.com')
		no_delete_item = Item.objects.create(list=list_, text='no delete')
		self.assertEqual(Item.objects.count(), 1)
		self.assertEqual(Item.objects.first().text, 'no delete')
		request.user = User.objects.create(email='not-owner@email.com')
		self.assertNotEqual(list_.owner, request.user)
		response = self.client.post('/lists/delete/item/%d/' % (no_delete_item.id,))
		self.assertEqual(Item.objects.count(), 1)
		self.assertEqual(Item.objects.first().text, 'no delete')

	def test_list_owner_is_saved_if_user_is_authenticated(self):
		request = HttpRequest()
		request.user = User.objects.create(email='a@b.com')
		request.POST['text'] = 'new list item'
		new_list(request)
		list_ = List.objects.all()[0]
		self.assertEqual(list_.owner, request.user)

	def test_invalid_input_renders_form_with_errors(self):
		response = self.post_invalid_input()
		self.assertIsInstance(response.context['form'], ExistingListItemForm)
		self.assertContains(response, escape(EMPTY_LIST_ERROR))
	
	def test_validation_errors_sent_back_to_home_page_template(self):
		response = self.client.post('/lists/new', data={'text': ''})
		self.assertEqual(List.objects.all().count(), 0)
		self.assertEqual(Item.objects.all().count(), 0)
		self.assertTemplateUsed(response, 'home.html')
		self.assertContains(response, escape(EMPTY_LIST_ERROR))

	def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
		list1 = List.objects.create()
		item1 = Item.objects.create(list=list1, text='textey')
		response = self.client.post(
			'/lists/%d/' % (list1.id,),
			data={'text': 'textey'}
		)

		expected_error = escape(DUPLICATE_ITEM_ERROR)
		self.assertContains(response, expected_error)
		self.assertTemplateUsed(response, 'list.html')
		self.assertEqual(Item.objects.all().count(), 1)


class MyListsTest(TestCase):


	def test_my_lists_url_renders_my_lists_template(self):
		User.objects.create(email='a@b.com')
		response = self.client.get('/lists/users/a@b.com/')
		self.assertTemplateUsed(response, 'my_lists.html')

	def test_passes_owner_to_template(self):
		user = User.objects.create(email='a@b.com')
		response = self.client.get('/lists/users/a@b.com/')
		self.assertEqual(response.context['owner'], user)

