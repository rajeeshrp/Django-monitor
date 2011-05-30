from django.contrib.admin.filterspecs import ChoicesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django_monitor.conf import STATUS_DICT

class MonitorFilter(ChoicesFilterSpec):
    """
    A custom filterspec to enable filter by monitor-status.
    Django development version has changes in store to break this!
    """
    def __init__(
        self, f, request, params, model, model_admin, field_path = None
    ):
        ChoicesFilterSpec.__init__(
            self, f, request, params, model, model_admin, field_path
        )
        self.lookup_kwarg = 'status'
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_choices = STATUS_DICT.keys()
        
    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }
        for val in self.lookup_choices:
            yield {
                'selected': smart_unicode(val) == self.lookup_val,
                'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                'display': STATUS_DICT[val]
            }

    def title(self):
        """ The title displayed above the filter"""
        return _("Moderation status")

