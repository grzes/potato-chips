# -*- coding: UTF-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from django.http import Http404
from django.core.urlresolvers import reverse

from google.appengine.api import users
from chips.models import Blog


def fullurl(url):
    return 'http://%s%s' % (settings.SITE_DOMAIN, url)


class UserBlogMiddleware(object):
    """Selects a user blog based on the subdomain."""
    def process_request(self, request):
        request.user = users.get_current_user()
        # find the logged in user's blog
        if request.user:
            user_blog = Blog.all().filter("owner =", request.user.user_id()).fetch(1)
            request.user_blog = user_blog[0] if user_blog else None
        else:
            request.user_blog = None

        # find the blog by subdomain
        host = request.get_host().lower()
        if host != settings.SITE_DOMAIN:
            prefix = host.split('.', 1)[0]
            request.blog = Blog.get_by_key_name(prefix)
            if not request.blog:
                if prefix == 'www':
                    return redirect(fullurl(request.get_full_path()))
                else:
                    raise Http404
        else:
            request.blog = None


def user_urls(request):
    """Context processor adding user login urls."""
    ctx = {
        'subdomain': request.blog is not None,
        'dash_url': fullurl(reverse('dash')),
        'latest_blogs': Blog.all().order('created').fetch(5)
    }
    if request.user:
        ctx['user'] = request.user
        ctx['user_blog'] = request.user_blog
        ctx['logout_url'] = users.create_logout_url(fullurl(reverse('postlist')))
    else:
        ctx['login_url'] = users.create_login_url(fullurl(reverse('dash')))
    return ctx


def require_user(with_blog=False):
    """A simple login require decorator."""
    def decorator(view):
        def newview(request, *args, **kwargs):
            # all user pager must be displayed without a prefix
            if request.blog:
                return redirect(fullurl(request.get_full_path()))
            if not request.user:
                return redirect(users.create_login_url(request.get_full_path()))

            if with_blog and not request.user_blog:
                return redirect(reverse("signup"))

            return view(request, *args, **kwargs)
        newview.__name__ = view.__name__
        return newview
    return decorator
