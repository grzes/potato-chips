# -*- coding: UTF-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from google.appengine.api import users


class UserBlogMiddleware(object):
    """Selects a user blog based on the subdomain."""
    def process_request(self, request):
        request.user = users.get_current_user()

        host = request.get_host().lower()
        request.user_blog = request.blog = None


def user_urls(request):
    """Context processor adding user login urls."""
    context = {}
    if request.user:
        context['user'] = request.user
        context['logout_url'] = users.create_logout_url(reverse('list'))
    else:
        context['login_url'] = users.create_login_url(reverse('dash'))
    return context


def require_user(with_blog=False):
    """A simple login require decorator."""
    def decorator(view):
        def newview(request, *args, **kwargs):
            if not request.user:
                return redirect(users.create_login_url(request.get_full_path()))
                
            if with_blog and not request.user_blog:
                return redirect(reverse("signup"))

            return view(*args, **kwargs)
        return newview
    return decorator
