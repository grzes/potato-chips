# -*- coding: UTF-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from google.appengine.api import users
from chips.models import Blog


class UserBlogMiddleware(object):
    """Selects a user blog based on the subdomain."""
    def process_request(self, request):
        request.user = users.get_current_user()
        if request.user:
            user_blog = Blog.all().filter("owner =", request.user.user_id()).fetch(1)
            request.user_blog = user_blog[0] if user_blog else None
        else:
            request.user_blog = None

        host_prefix = request.get_host().lower().split('.', 1)[0]
        if host_prefix != settings.SITE_DOMAIN:
            request.blog = Blog.get_by_key_name(host_prefix)


def user_urls(request):
    """Context processor adding user login urls."""
    context = {}
    if request.user:
        context['user'] = request.user
        context['user_blog'] = request.user_blog
        context['logout_url'] = users.create_logout_url(reverse('postlist'))
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

            return view(request, *args, **kwargs)
        newview.__name__ = view.__name__
        return newview
    return decorator
