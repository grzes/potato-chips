import logging
from django.views.generic import TemplateView
from django.conf import settings


class Home(TemplateView):
    template_name = "home.html"
    
    def get(self, request, *args, **kwargs):
        self.request.session['message'] = 'Sessions seem okay!'
        return super(Home, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['message'] = self.request.session.get('message', None)
        context['subdomain'] = self.request.META.get('HTTP_HOST', 'None')
        return context


def exception_test(request):
    logging.debug('Debug log')
    logging.warn('Warn log')
    logging.error('Error log')
    raise Exception()
    


    
