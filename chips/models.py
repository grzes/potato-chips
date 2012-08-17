# -*- coding: UTF-8 -*-
import logging
from django.conf import settings
from google.appengine.ext import db


class Blog(db.Model):
    owner = db.StringProperty(required=True)
    emailhash = db.StringProperty(required=True)
