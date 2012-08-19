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
from chips.models import Blog


settings.SITE_DOMAIN = 'testserver' # our blog selection middleware needs to match on the host



class UserBlog(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub(enable=not False)

    def login(self, email='', user_id=''):
        default_env = copy(testbed.DEFAULT_ENVIRONMENT)
        self.testbed.setup_env(overwrite=True, user_email=email, user_id=user_id)

    def tearDown(self):
        self.testbed.deactivate()

    def test_a_blogless_user(self):
        """Without a blog a user is redirected from his dash to the signup page"""
        self.login('test@example.com', user_id='1')
        client = Client()
        response = client.get(reverse('dash'))
        self.assertEqual('http://testserver'+reverse('signup'), response['location'])


if __name__ == '__main__':
    unittest.main()

