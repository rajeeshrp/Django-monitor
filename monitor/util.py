
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager

from monitor.middleware import get_current_user
from monitor.models import MonitorEntry, MONITOR_TABLE
from monitor.conf import (
    STATUS_DICT, PENDING_STATUS, APPROVED_STATUS, CHALLENGED_STATUS
)

def create_moderate_perms(app, created_models, verbosity, **kwargs):
    """ This will create moderate permissions for all registered models"""
    from django.contrib.auth.models import Permission

    from monitor import queued_models

    for model in queued_models():
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
            self._monitor_entry = MonitorEntry.objects.get_for_instance(self)
        return self._monitor_entry

    def _get_status_display(self):
        """ to display the moderation status in verbose """
        return STATUS_DICT[self._status]
    _get_status_display.short_description = status_name

    # Add custom manager & monitor_entry to class
    manager = CustomManager()
    cls.add_to_class(manager_name, manager)
    cls.add_to_class(monitor_name, property(_get_monitor_entry))
    cls.add_to_class(status_name, property(lambda self: self._status))
    cls.add_to_class(
        'get_status_display', _get_status_display
    )
    # We have a custom filter defined in monitor.filter to enable
    # filtering of model objects by their moderation status.
    # But `status` is not a real field and Django does not support filters
    # on non-fields as of now. Our way out is to attach the filter to some
    # other field which the developer may never include in list_filter.
    # I think, prmary key is the best option.
    # (Latest Django dev-version has undergone changes to allow non-fields.)
    cls._meta.get_field(cls._meta.pk.attname).monitor_filter = True

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

    # Create corresponding monitor entry
    if kwargs.get('created', None):
        MonitorEntry.objects.create(
            status = status, content_object = instance,
            timestamp = datetime.now()
        )

        # Moderate related objects too... 
        from monitor import model_from_queue
        model = model_from_queue(instance.__class__)
        if model:
            for rel_name in model['rel_fields']:
                moderate_rel_objects(getattr(instance, rel_name), status, user)

def moderate_rel_objects(given, status, user = None):
    """
    `given` can either be any model object or a queryset. Moderate given
    object(s) and all specified related objects.
    TODO: Permissions must be checked before each iteration.
    """
    from monitor import model_from_queue
    # Not sure how we can find whether `given` is a queryset or object.
    # Now assume `given` is a queryset/related_manager if it has 'all'
    if not given:
        # given may become None. Stop there.
        return
    if hasattr(given, 'all'):
        qset = given.all()
        for obj in qset:
            me = MonitorEntry.objects.get_for_instance(obj)
            me.moderate(status, user)
            model = model_from_queue(qset.model)
            if model:
                for rel_name in model['rel_fields']:
                    moderate_rel_objects(getattr(obj, rel_name), status, user)
    else:
        me = MonitorEntry.objects.get_for_instance(given)
        me.moderate(status, user)
        model = model_from_queue(given.__class__)
        if model:
            for rel_name in model['rel_fields']:
                moderate_rel_objects(getattr(given, rel_name), status, user)

