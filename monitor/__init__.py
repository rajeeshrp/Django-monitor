__author__ = "Rajeesh Nair"
__version__ = "0.1.0a"
__copyright__ = "Copyright (c) 2011 Rajeesh"
__license__ = "BSD"

from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager, signals

from monitor.middleware import get_current_user
from monitor.models import MonitorEntry

_queue = {}

def is_in_queue(model):
    """ Whether the given model is put in queue or not."""
    return _queue.has_key(model)

PENDING_STATUS = 'IP'
APPROVED_STATUS = 'AP'
CHALLENGED_STATUS = 'CH'

MONITOR_TABLE = MonitorEntry._meta.db_table

def nq(
    model, rel_fields = [], manager_name = 'objects',
    status_name = 'status', monitor_name = 'monitor_entry', base_manager = None
):
    """ Register(enqueue) the model for moderation."""
    if not is_in_queue(model):
        signals.post_save.connect(save_handler, sender = model)
        add_fields(model, manager_name, status_name, monitor_name, base_manager)
        _queue[model] = {'model': model, 'rel_fields': rel_fields}

def dq(model):
    """ Unregister (dequeue) the registered model."""
    return _queue.pop(model, None)

def create_moderate_perms(app, created_models, verbosity, **kwargs):
    """ This will create moderate permissions for all registered models"""
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    mod_models = _queue.keys()
    for model in mod_models:
        ctype = ContentType.objects.get_for_model(model)
        codename = 'moderate_%s' % model._meta.object_name.lower()
        name = u'Can moderate %s' % model._meta.verbose_name_raw
        p, created = Permission.objects.get_or_create(
            codename = codename,
            content_type__pk = ctype.id,
            defaults = {'name': name, 'content_type': ctype}
        )
        if created and verbosity >= 2:
            print "Adding permission '%s'" % p

signals.post_syncdb.connect(
    create_moderate_perms,
    dispatch_uid = "django-monitor.create_moderate_perms"
)

def add_fields(cls, manager_name, status_name, monitor_name, base_manager):
    """ Add additional fields like status to moderated models"""
    # Inheriting from old manager
    if base_manager is None:
        if hasattr(cls, manager_name):
            base_manager = getattr(cls, manager_name).__class__
        else:
            base_manager = Manager
    # Queryset inheriting from manager's Queryset
    base_queryset = base_manager().get_query_set().__class__

    class CustomQuerySet(base_queryset):
        """ Chainable queryset for checking status """
       
        def _by_status(self, field_name, status):
            """ Filter queryset by given status"""
            where_clause = '%s = %%s' % (field_name)
            return self.extra(where = [where_clause], params = [status])

        def approved(self):
            """ All approved objects"""
            return self._by_status(status_name, APPROVED_STATUS)

        def exclude_approved(self):
            """ All not-approved objects"""
            where_clause = '%s != %%s' % (status_name)
            return self.extra(
                where = [where_clause], params = [APPROVED_STATUS]
            )

        def pending(self):
            """ All pending objects """
            return self._by_status(status_name, PENDING_STATUS)

        def challenged(self):
            """ All challenged objects """
            return self._by_status(status_name, CHALLENGED_STATUS)

    class CustomManager(base_manager):
        """ custom manager that adds parameters and uses custom QuerySet """

        # use_for_related_fields is read when the model class is prepared
        # because CustomManager isn't set on the class at the time
        # this really has no effect, but is set to True because we are going
        # to hijack cls._default_manager later
        use_for_related_fields = True

        # add monitor_id and status_name attributes to the query
        def get_query_set(self):
            # parameters to help with generic SQL
            db_table = self.model._meta.db_table
            pk_name = self.model._meta.pk.attname
            content_type = ContentType.objects.get_for_model(self.model).id

            # extra params - status and id of object (for later access)
            select = {
                '_monitor_id': '%s.id' % MONITOR_TABLE,
                '_status': '%s.status' % MONITOR_TABLE,
            }
            where = [
                '%s.content_type_id=%s' % (MONITOR_TABLE, content_type),
                '%s.object_id=%s.%s' % (MONITOR_TABLE, db_table, pk_name)
            ]
            tables = [MONITOR_TABLE]

            # build extra query then copy model/query to a CustomQuerySet
            q = super(CustomManager, self).get_query_set().extra(
                select = select, where = where, tables = tables
            )
            return CustomQuerySet(self.model, q.query)

    def _get_monitor_entry(self):
        """ accessor for monitor_entry that caches the object """
        if not hasattr(self, '_monitor_entry'):
            self._monitor_entry = Monitor.objects.get(pk = self._monitor_id)
        return self._monitor_entry

    # Add custom manager & monitor_entry to class
    manager = CustomManager()
    cls.add_to_class(manager_name, manager)
    cls.add_to_class(monitor_name, property(_get_monitor_entry))
    cls.add_to_class(status_name, property(lambda self: self._status))

    # Copy manager to default_class
    cls._default_manager = manager

def save_handler(sender, instance, **kwargs):
    """
    After saving an object in moderated class, do the following:
    1. Create a corresponding monitor entry.
    2. Auto-moderate objects if enough permissions are available.
    3. Moderate specified related objects too.
    """
    # Auto-moderation
    user = get_current_user()
    opts = instance.__class__._meta
    mod_perm = '%s.moderate_%s' % (
        opts.app_label.lower(), opts.object_name.lower()
    )
    if user and user.has_perm(mod_perm):
        status = APPROVED_STATUS
    else:
        status = PENDING_STATUS

    # Corresponding monitor entry
    if kwargs.get('created', None):
        me = MonitorEntry(
            status = status, content_object = instance,
            timestamp = datetime.now()
        )
        me.save()

