from django.db import models
from django.shortcuts import resolve_url
from django.conf import settings


class List(models.Model):
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

	def get_absolute_url(self):
		return resolve_url('view_list', self.id)

	@property
	def name(self):
		return self.item_set.all()[0].text


class Item(models.Model):
	text = models.TextField()
	list = models.ForeignKey(List)


	class Meta:
		ordering = ('id',)
		unique_together = ('list', 'text')


	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


	def __str__(self):
		return self.text
