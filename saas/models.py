# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# below models can be extended according to the specific saas uses cases. This is boiler plate only

class Plan(models.Model):
	PLAN_FREE_TIER_ID       = 1
	PLAN_FREE_DURATION_DAYS = 15

	name              = models.CharField(max_length=255)
	description       = models.CharField(max_length=255, null=True, blank=True)
	duration_days     = models.IntegerField(default=PLAN_FREE_DURATION_DAYS)
	usd_price         = models.DecimalField(max_digits=6, decimal_places=2)
	created_at        = models.DateTimeField(auto_now_add=True)
	last_updated_on   = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.name

class Business(models.Model):
	name                     = models.CharField(max_length=255)
	created_at               = models.DateTimeField(auto_now_add=True)
	last_updated_on          = models.DateTimeField(auto_now=True)
	is_active                = models.BooleanField(default=True)
	api_key                  = models.CharField(max_length=50, null=True)

	def __unicode__(self):
		return "{}_{}".format(self.id, self.name)


class Subscription(models.Model):
	business                 = models.ForeignKey(Business)
	plan                     = models.ForeignKey(Plan)
	is_active                = models.BooleanField(default=False)
	created_at               = models.DateTimeField(auto_now_add=True)
	start_time               = models.DateTimeField()
	end_time                 = models.DateTimeField()
	last_updated_on          = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.business.__unicode__() + "_" + str(self.id)

class BusinessTeamMember(models.Model):
	business            = models.ForeignKey(Business)
	user                = models.ForeignKey(User)
	activation_key      = models.CharField(max_length=36)
	created_at          = models.DateTimeField(auto_now_add=True)
	last_updated_on     = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('business', 'user',)

	def __unicode__(self):
		return "{}_{}".format(self.business.id, self.user.username)
