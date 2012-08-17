# -*- coding: UTF-8 -*-
import logging
import hashlib

from django.conf import settings
from django import forms

from google.appengine.ext import db

from chips.models import Blog


class SignupForm(forms.Form):
    """Signup for a blog with a unique url."""
    url = forms.SlugField(min_length=5, max_length=30)

    def __init__(self, *a, **kw):
        self.owner = kw.pop('owner')
        super(SignupForm, self).__init__(*a, **kw)

    def clean(self):
        # Because of the transactional nature of the availability check, the url
        # will be reserved here
        cleaned_data = super(SignupForm, self).clean()
        url = cleaned_data.get("url")

        def tx(url, user_id, email_hash):
            blog = Blog.get_by_key_name(url)
            if blog:
                raise forms.ValidationError(_("The chosen url is already taken"))

            blog = Blog(key_name=url, owner=user_id, emailhash=email_hash)
            blog.put()

        if url:
            db.run_in_transaction(tx, 
                url, 
                self.owner.user_id(),
                hashlib.md5(self.owner.email()).hexdigest())

