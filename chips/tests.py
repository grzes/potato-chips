import os
from copy import copy
from pypath import pypath;pypath()
import unittest
from django.test.client import Client
from django.conf import settings

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

from django.core.urlresolvers import reverse
from chips.models import Blog, Post
from chips.users import fullurl


settings.SITE_DOMAIN = 'testserver' # our blog selection middleware needs to match on the host

def blogurl(blog):
    return 'http://%s.%s/' % (blog, settings.SITE_DOMAIN)


class TestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.client = Client()

    def login(self, email='', user_id=''):
        self.testbed.setup_env(overwrite=True, user_email=email, user_id=user_id)

    def tearDown(self):
        self.testbed.deactivate()


class UserBlog(TestCase):
    def test_a_blogless_user(self):
        """Without a blog a user is redirected from his dash to the signup page"""
        self.login('blogless@example.com', user_id='1')
        response = self.client.get(reverse('dash'))
        self.assertEqual('http://testserver'+reverse('signup'), response['location'])

    def test_blogging_user(self):
        """A user with a blog can view their dash."""
        self.login('blog@example.com', user_id='2')
        Blog.create(key_name='blog', owner='2', emailhash='#')
        response = self.client.get(reverse('dash'))
        self.assertEqual(200, response.status_code)


class BlogVisibility(TestCase):
    def setUp(self):
        super(BlogVisibility, self).setUp()

        self.b1 = Blog.create(key_name='john', owner='1', emailhash='#')
        self.b2 = Blog.create(key_name='bob', owner='2', emailhash='#')

    def create_posts(self):
        self.p1 = Post.create(author=self.b1, text="t1", friends=self.b1.friends())
        self.p2 = Post.create(author=self.b2, text="t2", friends=self.b2.friends())
        self.p3 = Post.create(author=self.b1, text="t3", friends=self.b1.friends())

    def test_dash_postlist(self):
        """Only see own posts in the dash"""
        self.create_posts()
        self.login('john.example.com', user_id='1')
        response = self.client.get(reverse('dash'))
        self.assertEqual(['t3', 't1'], [p.text for p in response.context['posts']])

    def test_following_postlist(self):
        """After following someone you can see their posts"""
        self.b1.follow(self.b2)
        self.create_posts()
        self.login('john.example.com', user_id='1')
        response = self.client.get(reverse('dash'))
        self.assertEqual(['t3', 't2', 't1'], [p.text for p in response.context['posts']])


    def test_req_following_postlist(self):
        """After following someone you can see their posts (follow via request)"""
        self.login('john.example.com', user_id='1')
        self.client.post(reverse('follow', args=('bob',)))
        self.create_posts()
        response = self.client.get(reverse('dash'))
        self.assertEqual(['t3', 't2', 't1'], [p.text for p in response.context['posts']])

        # but john's blog still only shows his posts
        response = self.client.get(blogurl('john'), SERVER_NAME='john')
        self.assertEqual(['t3', 't1'], [p.text for p in response.context['posts']])


    def test_blog_postlist(self):
        """The blog subdomains allow anyone to view the given blog's posts."""
        self.create_posts()
        response = self.client.get(blogurl('bob'), SERVER_NAME='bob')
        self.assertEqual(['t2'], [p.text for p in response.context['posts']])

        response = self.client.get(blogurl('john'), SERVER_NAME='john')
        self.assertEqual(['t3', 't1'], [p.text for p in response.context['posts']])

if __name__ == '__main__':
    unittest.main()

