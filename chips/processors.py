from google.appengine.api import users
from django.core.urlresolvers import reverse


def user_urls(request):
	d = {}
	if request.user:
		d['user'] = request.user
		d['logout_url'] = users.create_logout_url(reverse('list'))
	else:
		d['login_url'] = users.create_login_url(reverse('dash'))
	return d
