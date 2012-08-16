import logging
from django.conf import settings

from django.shortcuts import render


def home(request):
    request.session['message'] = 'Sessions seem okay!'
    return render(request, "home.html", {
            'message': request.session.get('message', None),
            'subdomain': request.META.get('HTTP_HOST', None)
        })


def exception_test(request):
    logging.debug('Debug log')
    logging.warn('Warn log')
    logging.error('Error log')
    raise Exception()
    


    
