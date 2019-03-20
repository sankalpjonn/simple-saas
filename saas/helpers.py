import uuid, os, hashlib

from django.contrib.auth.models import User
from django.conf import settings

def generate_activation_key():
	return str(uuid.uuid4())

def get_md5_hash(s):
	m = hashlib.md5()
	m.update(s)
	return m.hexdigest()

def get_sorted_keys_from_dict(d):
	keys = d.keys()
	keys.sort()
	return keys

def get_or_create_user(email, password=generate_activation_key()):
	try:
		return User.objects.get(username=email), False
	except User.DoesNotExist:
		return User.objects.create_user(email, email, password), True
