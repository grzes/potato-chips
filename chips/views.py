import logging
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


def list(request):
    """The blog view, if no user logged in or chosen display the home page."""
    request.session['message'] = 'Sessions seem okay!'
    return render(request, "home.html", {
            'message': request.session.get('message', None),
        })


def dash(request):
    """Users dashboard.
    It's like the main blog view but shows friend's posts."""
    return redirect(reverse('list'))


def exception_test(request):
    logging.debug('Debug log')
    logging.warn('Warn log')
    logging.error('Error log')
    raise Exception()
    


    
