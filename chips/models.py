# -*- coding: UTF-8 -*-
import logging
from django.conf import settings
from google.appengine.ext import db


class Blog(db.Model):
    """A user profile of sorts, used only for the storing emailhash."""
    owner = db.StringProperty(required=True)
    emailhash = db.StringProperty(required=True)

    def friends(self):
        return Friends.get_by_key_name('friends', parent=self).f

    @classmethod
    def create(cls, **properties):
        blog = cls(**properties)
        blog.put()

        # Create the initial friends list
        Friends(key_name='friends', parent=blog, f=[blog.key()]).put()


class Friends(db.Model):
    """A list of "followed" blogs.

    Stored as a separate entity to avoid deserialization unless we need it."""
    f = db.ListProperty(db.Key, required=True)


class Post(db.Model):
    """Blog post."""
    author = db.ReferenceProperty(Blog)
    text = db.TextProperty()
    deleted = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True, required=True)

    @classmethod
    @db.transactional
    def create(cls, author, text, friends):
        """Creating a blogpost along a reader index."""
        post = cls(author=author, text=text)
        post.put()
        PostIndex(key_name='i', parent=post, created=post.created, b=friends).put()


class PostIndex(db.Model):
    """An index entity for listing blogposts."""
    created = db.DateTimeProperty()
    b = db.ListProperty(db.Key, required=True)