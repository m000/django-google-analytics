from django import template
from django.db import models
from django.contrib.sites.models import Site

from django.template import Variable, Context, loader

register = template.Library()
Analytics = models.get_model('googleanalytics', 'analytics')

def do_get_analytics(parser, token):
    contents = token.split_contents()
    # Evaluation of arguments is now made during rendering.
    return AnalyticsNode(contents)

class AnalyticsNode(template.Node):
    def __init__(self, ttag_arguments):
        # set defaults
        self.code = None
        self.template_name = 'google_analytics/%s_template.html' % ttag_arguments[0]

        # create variables to be evaluated during rendering phase
        self.arguments = ttag_arguments[1:]

        
    def render(self, context):
        for arg in self.arguments:
            # arguments parsing & evaluation
            key, sep, val = arg.partition('=')
            if sep:
                setattr(self, key, Variable(val).resolve(context))
                print getattr(self, key)
            else:
                # No separator found. Treat argument as code.
                # Unless the argument is quoted, it will be looked-up in the context.
                # Because of this, a VariableDoesNotExist error is generated for unquoted arguments.
                self.code = Variable(arg).resolve(context).strip()

        if not self.code:
            # No code has been specified as argument. Retrieve the one associated with the current site.
            current_site = Site.objects.get_current()
            current_site_analytics = current_site.analytics_set.all()
            if current_site_analytics:
                self.code = current_site_analytics[0].analytics_code.strip()
                # An empty code is associated with the site. Render nothing.
                if not self.code: return ''
            else:
                # No code associated with the site. Render nothing.
                return ''

        return loader.get_template(self.template_name).render(Context({
            'analytics_code': self.code,
        }))
        
register.tag('analytics', do_get_analytics)
register.tag('analytics_async', do_get_analytics)

