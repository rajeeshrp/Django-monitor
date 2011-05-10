
from monitor import _queue
from monitor.models import MonitorEntry

def moderate_rel_objects(given, status, user = None):
    """
    `given` can either be any model object or a queryset. Moderate given
    object(s) and all specified related objects.
    TODO: Permissions must be checked before each iteration.
    """
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
            rel_fields = _queue[qset.model]['rel_fields']
            for rel_name in rel_fields:
                moderate_rel_objects(getattr(obj, rel_name), status, user)
    else:
        me = MonitorEntry.objects.get_for_instance(given)
        me.moderate(status, user)
        rel_fields = _queue[given._meta.model]['rel_fields']
        for rel_name in rel_fields:
            moderate_rel_objects(getattr(given, rel_name), status, user)

