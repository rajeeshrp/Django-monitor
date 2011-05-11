
.. _`usage`:

==========
How to use
==========

For developers
===============

Registration
-------------
Register the model for moderation using ``monitor.nq``.

**Example** ::

    import monitor
    # Your model here
    monitor.nq(YOUR_MODEL)

The full signature is like this: ::

    monitor.nq(model, [rel_fields=[], manager_name='objects', status_name='status', monitor_name='monitor_entry', base_manager=None])

The supported arguments are as follows:

+ ``rel_fields``: List of related fields to be moderated along with this.
  This is useful when your model is foreign key to some other model and
  those model objects are added inline to the former. So when you check
  and approve the former model object, you might have verified all those
  inline objects too and so they too can be approved along with it.
  See the example:
  ::

    # In admin.py
    class BookAdmin(MonitorAdmin):
        inlines = ['SupplementInline',]

    # In models.py
    class Book(model.Model):
        name = models.CharField(max_length = 100)

    class Supplement(models.Model):
        name = models.CharField(max_length = 100)
        book = models.ForeignKey(Book, related_name = 'supplements')

    monitor.nq(Book, rel_fields = ['supplements'])

+ ``manager_name``:  We assume that ``objects`` is the name of the manager
  instance of your model. If you want to use a different name for the
  instance, specify the name with ``manager_name`` parameter.

+ ``status_name``: By default, the moderation status field is named as
  `status`. If you prefer some other name, specify it.

+ ``monitor_name``: A MonitorEntry object will be created to monitor each
  object of moderated model. By default, it is referred as `monitor_entry``.
  If you prefer some other name, specify it.

+ ``base_manager``: Django-monitor replaces the manager of moderated model
  with a special manager class derived from the original. Leave this as None
  if you want to use the default manager class. If you have written a custom
  manager for the model, you may specify it here.

Special model-admin class
--------------------------
Inherit the MonitorAdmin instead of django's built-in ModelAdmin for moderated
models.::

  # in your admin.py
  from monitor.admin import MonitorAdmin
  class YourModelAdmin(MonitorAdmin):
      pass

Data-protection
----------------
``protected_fields`` in model-admin can be used to prevent users from
changing certain fields in approved objects. Specify the field names as you
do with ``readonly_fields``.::

  # in your admin.py
  class YourModelAdmin(MonitorAdmin):
      protected_fields = ['field1', 'field2']

For admin-users
===============

Permission
-----------
Django-monitor creates a moderate permission for each moderated model. Only
those users with required permission can moderate any object of a particular
model. The superuser or one with enough permissions must assign those
permissions to the appropriate users.

Moderation by Actions
-----------------------
Moderation is performed through change-list actions,  ``approve``, ``challenge``
and ``reset to pending``. If the manager selects few objects, choose the action
``approve`` and press ``Go``, those objects will get approved. Similarly, one
can challenge some objects too. Once some objects get challenged, the
non-managers with edit permissions may check them again and make required
corrections. After that, they can reset the status to ``In pending`` so that
their manager gets to verify them again.

