# -*- coding: UTF-8 -*-
import logging
import hashlib

from django.conf import settings
from django import forms

from google.appengine.ext import db

from chips.models import Blog, Post


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
                raise forms.ValidationError("The chosen url is already taken")

            Blog.create(key_name=url, owner=user_id, emailhash=email_hash)

        if url:
            db.run_in_transaction(tx, 
                url.lower(), 
                self.owner.user_id(),
                hashlib.md5(self.owner.email()).hexdigest())


class PostForm(forms.Form):
    """Blog post creation form."""
    text = forms.CharField(max_length=450, widget=forms.Textarea) 

    def __init__(self, *a, **kw):
        self.blog = kw.pop('blog')
        super(PostForm, self).__init__(*a, **kw)

    def save(self):
        Post.create(author=self.blog,
            text=self.cleaned_data['text'],
            friends=self.blog.friends()
        )


class EditForm(forms.Form):
    """Post deletion and edit form."""
    text = forms.CharField(max_length=450, widget=forms.Textarea)
    delete = forms.BooleanField(required=False)

    def __init__(self, *a, **kw):
        self.post = kw.pop('post')
        kw['initial'] = {'text': self.post.text}
        super(EditForm, self).__init__(*a, **kw)

    def save(self):
        if self.cleaned_data['delete']:
            self.post.deleted = True
        else:
            self.post.text = self.cleaned_data['text']
        self.post.put()
