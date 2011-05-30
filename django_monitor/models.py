from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime

from django_monitor.conf import (
    STATUS_DICT, PENDING_STATUS, APPROVED_STATUS, CHALLENGED_STATUS
)
STATUS_CHOICES = STATUS_DICT.items()

class MonitorEntryManager(models.Manager):
    """ Custom Manager for MonitorEntry"""

    def get_for_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        try:
            mo = MonitorEntry.objects.get(content_type = ct, object_id = obj.pk)
            return mo
        except MonitorEntry.DoesNotExist:
            pass

class MonitorEntry(models.Model):
    """ Each Entry will monitor the status of one moderated model object"""
    objects = MonitorEntryManager()
    
    timestamp = models.DateTimeField(
        auto_now_add = True, blank = True, null = True
    )
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES)
    status_by = models.ForeignKey(User, blank = True, null = True)
    status_date = models.DateTimeField(blank = True, null = True)
    notes = models.CharField(max_length = 100, blank = True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'django_monitor'
        verbose_name = 'moderation Queue'
        verbose_name_plural = 'moderation Queue'

    def __unicode__(self):
        return "[%s] %s" % (self.get_status_display(), self.content_object)

    def get_absolute_url(self):
        if hasattr(self.content_object, "get_absolute_url"):
            return self.content_object.get_absolute_url()

    def _moderate(self, status, user, notes = ''):
        from django_monitor import post_moderation
        self.status = status
        self.status_by = user
        self.status_date = datetime.datetime.now()
        self.notes = notes
        self.save()
        # post_moderation signal will be generated now with the associated
        # object as the ``instance`` and its model as the ``sender``.
        sender_model = self.content_type.model_class()
        instance = self.content_object
        post_moderation.send(sender = sender_model, instance = instance)

    def approve(self, user = None, notes = ''):
        """Deprecated. Approve the object"""
        self._moderate(APPROVED_STATUS, user, notes)

    def challenge(self, user = None, notes = ''):
        """Deprectaed. Challenge the object """
        self._moderate(CHALLENGED_STATUS, user, notes)

    def reset_to_pending(self, user = None, notes = ''):
        """Deprecated. Reset status from Challenged to pending"""
        self._moderate(PENDING_STATUS, user, notes)

    def moderate(self, status, user = None, notes = ''):
        """
        Why a separate public method?
        To use when you're not sure about the status given
        """
        if status in STATUS_DICT.keys():
            self._moderate(status, user, notes)

    def is_approved(self):
        """ Deprecated"""
        return self.status == APPROVED_STATUS

    def is_pending(self):
        """ Deprecated."""
        return self.status == PENDING_STATUS

    def is_challenged(self):
        """ Deprecated."""
        return self.status == CHALLENGED_STATUS

MONITOR_TABLE = MonitorEntry._meta.db_table

