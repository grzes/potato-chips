# -*- coding: UTF-8 -*-
import logging
from google.appengine.ext import db


def prefetch_refprops(entities, *props):
    """Fetching reference properties for a given list of objects in a single db get.

    credit: http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine
    """
    fields = [(entity, prop) for entity in entities for prop in props]
    ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for (entity, prop), ref_key in zip(fields, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
