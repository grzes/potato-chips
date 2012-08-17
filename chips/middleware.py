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
        request.blog = host
