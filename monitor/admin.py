
from django.contrib import admin

from monitor.actions import approve_selected, challenge_selected
from monitor.actions import reset_to_pending
from monitor import APPROVED_STATUS

class MonitorAdmin(admin.ModelAdmin):
    """Use this for monitored models."""

    # Which fields are to be made readonly after approval.
    protected_fields = ()

    def is_monitored(self):
        """Returns whether the underlying model is monitored or not."""
        from monitor import is_in_queue
        return is_in_queue(self.model)

    def get_readonly_fields(self, request, obj = None):
        """ Overridden to include protected_fields as well."""
        if self.is_monitored() and obj is not None and obj.status == APPROVED_STATUS:
            return self.readonly_fields + self.protected_fields
        return self.readonly_fields

    def get_actions(self, request):
        """ For monitored models, we need 3 more actions."""
        actions = super(MonitorAdmin, self).get_actions(request)
        mod_perm = '%s.moderate_%s' % (
            self.opts.app_label.lower(), self.opts.object_name.lower()
        )
        change_perm = mod_perm.replace('moderate', 'change')
        if request.user.has_perm(mod_perm):
            descr = getattr(
                approve_selected, 'short_description', 'approve selected'
            )
            actions.update({
                'approve_selected': (approve_selected, 'approve_selected', descr)
            })
            descr = getattr(
                challenge_selected, 'short_description', 'challenge selected'
            )
            actions.update({
                'challenge_selected': (challenge_selected, 'challenge_selected', descr)
            })
        if request.user.has_perm(change_perm):
            descr = getattr(
                reset_to_pending, 'short_description', 'reset to pending'
            )
            actions.update({
                'reset_to_pending': (reset_to_pending, 'reset_to_pending', descr)
            })
        return actions

    def has_moderate_permission(self, request):
        """
        Returns true if the given request has permission to moderate objects
        of the model corresponding to this model admin.
        """
        mod_perm = '%s.moderate_%s' % (
            self.opts.app_label.lower(), self.opts.object_name.lower()
        )
        return request.user.has_perm(mod_perm)

