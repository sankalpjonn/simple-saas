from rest_framework import permissions
from django.contrib.auth.models import User
from .models import *

class IsBusiness(permissions.BasePermission):

	def has_permission(self, request, view):
		safe_methods = ['POST', 'GET', 'PATCH']

		if request.user.is_anonymous():
			return False
		if BusinessTeamMember.objects.filter(
			user=request.user).exists():
			return request.method in safe_methods
