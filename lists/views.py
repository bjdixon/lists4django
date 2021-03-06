from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import AnonymousUser
from lists.models import Item, List
from django.core.exceptions import ValidationError, PermissionDenied
from lists.forms import ExistingListItemForm, ItemForm


# Create your views here.
def home_page(request):
	return render(request, 'home.html', {'form': ItemForm()})

def view_list(request, list_id):
	list_ = List.objects.get(id=list_id)
	form = ExistingListItemForm(for_list=list_, data=request.POST or None)
	if form.is_valid():
		form.save()
		return redirect(list_)
	return render(request, 'list.html', {'list': list_, "form": form})

def new_list(request):
	form = ItemForm(data=request.POST)
	if form.is_valid():
		list_ = List.objects.create()
		if not isinstance(request.user, AnonymousUser):
			list_.owner = request.user
			list_.save()
		form.save(for_list=list_)	
		return redirect(list_)
	else:
		return render(request, 'home.html', {"form": form})

def add_item(request, list_id):
	list_ = List.objects.get(id=list_id)
	Item.objects.create(text=request.POST['text'], list=list_)
	return redirect('/lists/%d/' % (list_.id,))

def delete_item(request, item_id):
	list_item = Item.objects.get(id=item_id)
	list_ = list_item.list
	if request.user == list_.owner:
		list_item.delete()
		return redirect('/lists/%d/' % (list_.id,))
	raise PermissionDenied
	return redirect('/lists/error/403/')

def error_403(request):
	return HttpResponseForbidden(render_to_string('error_403.html'))

def my_lists(request, email):
	owner = User.objects.get(email=email)
	return render(request, 'my_lists.html', {'owner': owner})

