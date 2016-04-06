from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

# Create your models here.
from django.utils.timezone import now


class Follow(models.Model):
	"""
	Define Follow model which will hold list of follower and following
	and time when he/she started following
	"""
	follower = models.ForeignKey(User, related_name='follower', db_index=True)
	following = models.ForeignKey(User, related_name='following', db_index=True)
	date = models.DateTimeField(default=now)

	class Meta:
		unique_together = ('follower', 'following')


class Twit(models.Model):
	"""
	Twit model which holds twit data
	"""
	content = models.CharField(max_length=140)
	posted_on = models.DateTimeField(default=now)
	updated_on = models.DateTimeField(default=now, db_index=True)
	author = models.ForeignKey(User, db_index=True)

	def save(self, *args, **kwargs):

		# At inital set both as current time

		if self.posted_on is None:
			self.posted_on = now()
			self.updated_on = now()
		else:
			self.updated_on = now()

		super(Twit, self).save(*args, **kwargs)

