from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime

STATUS_CHOICES = [
    ('IP', "In Pending"),
    ('AP', "Approved"),
    ('CH', "Challenged")
]

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
        app_label = 'monitor'

    def __unicode__(self):
        return "[%s] %s" % (self.get_status_display(), self.content_object)

    def get_absolute_url(self):
        if hasattr(self.content_object, "get_absolute_url"):
            return self.content_object.get_absolute_url()

    def _moderate(self, status, user, notes = None):
        self.status = status
        self.status_by = user
        self.status_date = datetime.datetime.now()
        self.notes = notes
        self.save()

    def approve(self, user, notes = ''):
        """ Approve the object"""
        self._moderate('AP', user, notes)

    def challenge(self, user, notes = ''):
        """ Challenge the object """
        self._moderate('CH', user, notes)

    def moderate(self, status, user, notes = ''):
        """
        Why a separate public method?
        To use when you're not sure about the status given
        """
        self._moderate(status, user, notes)

