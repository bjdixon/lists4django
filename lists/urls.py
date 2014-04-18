from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
	url(r'^(\d+)/$', 'lists.views.view_list', name='view_list'),
	url(r'^new$', 'lists.views.new_list', name='new_list'),
	url(r'^delete/item/(\d+)/$', 'lists.views.delete_item', name='delete_item'),
	url(r'^users/(.+)/$', 'lists.views.my_lists', name='my_lists'),
	url(r'^error/403/$', 'lists.views.error_403', name='error_403'),
)

