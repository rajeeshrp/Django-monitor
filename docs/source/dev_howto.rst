
.. _`dev_howto`:

============================
How to use (for developers)
============================

Registration (Enqueue)
======================

Register the model for moderation using ``django_monitor.nq``.

**Example** ::

    import django_monitor
    # Your model here
    django_monitor.nq(YOUR_MODEL)

The full signature is... ::

    django_monitor.nq(
        model, [rel_fields = [], can_delete_approved = True,
        manager_name = 'objects', status_name = 'status',
        monitor_name = 'monitor_entry', base_manager = None]
    )

``model`` is the only required argument. Other optional arguments follow:

+ ``rel_fields``: List of related fields to be moderated along with this.
  Read more details below at :ref:`dev_howto_rel_moderation`.

+ ``can_delete_approved``: To prevent admin-users from deleting approved
  objects, set this to ``False``. Default is ``True``. Read more details
  below at :ref:`dev_howto_data_protect`.

+ ``manager_name``:  We assume that ``objects`` is the name of the manager
  instance of your model. If you want to use a different name for the
  instance, specify the name with ``manager_name`` parameter.

+ ``status_name``: By default, the moderation status field is named as
  `status`. If you prefer some other name, specify it.

+ ``monitor_name``: A MonitorEntry object will be created to monitor each
  object of moderated model. By default, it is referred as `monitor_entry`.
  If you prefer some other name, specify it.

+ ``base_manager``: Django-monitor replaces the manager of moderated model
  with a special manager class derived from the original. Leave this as None
  if you want to use the default manager class. If you have written a custom
  manager for the model, you may specify it here.

Special model-admin class
==========================

We build admin classes for moderated models using ``MonitorAdmin`` instead of
django's built-in ``ModelAdmin``. Always remember to inherit from
``MonitorAdmin`` when you define model-admin class for your moderated model.

::

    # in your admin.py
    from django_monitor.admin import MonitorAdmin
    class YourModelAdmin(MonitorAdmin):
        pass

.. _`dev_howto_rel_moderation`:

Related moderation
====================

This is useful when your model is foreign key to some other model and those
model objects are added inline to the former. So when you check and approve
the former model object, you might have verified all those inline objects too
and so they too can be approved along with it. See the **example**: ::

    # In admin.py
    class BookAdmin(MonitorAdmin):
        inlines = ['SupplementInline',]

    # In models.py
    class Book(model.Model):
        name = models.CharField(max_length = 100)

    class Supplement(models.Model):
        name = models.CharField(max_length = 100)
        book = models.ForeignKey(Book, related_name = 'supplements')

    django_monitor.nq(Book, rel_fields = ['supplements'])
    django_monitor.nq(Supplement)

Remember that both models should be put in moderation queue.

.. _`dev_howto_data_protect`:

Data-protection
================

Business organizations may require their applications to prevent admin users
from modifying or deleting approved objects. We allow developers to enable
that using two parameters, ``protected_fields`` and ``can_delete_approved``.

``MonitorAdmin.protected_fields`` can be used to prevent users from changing
values of certain fields in approved objects. Specify the field names as you
would do with ``readonly_fields``. See the **example** below: ::

    # in your admin.py
    class YourModelAdmin(MonitorAdmin):
        protected_fields = ['field1', 'field2']

``can_delete_approved`` is an optional parameter you pass to 
``django_monitor.nq``. Its default value is ``True`` which allows users to
delete all objects. If this is set to ``False``, admin-user can not delete
an object once it is approved. Deleting either un-moderated or pending or
challenged objects can be done as usual. You still can delete approved
objects by code or from the django-shell.

Creation of objects by code
============================

The above sections shared tips on how to prepare your application for
moderation by admin-users. What about the objects you create by code? All
objects created by code will be in pending status by default. You can moderate
them by code using the following public methods of the moderated model:

.. note::

   ``user`` is an optional parameter in all those methods described below.
   Please pass the current user to the methods in all possible cases.
   ``request.user`` can be used for this whenever ``request`` is available.
   Otherwise, use the function, ``django_monitor.middleware.get_current_user``.

#. approve:
    ::

        approve([user = None, notes = ''])

#. challenge:
    ::

        challenge([user = None, notes = ''])

#. reset_to_pending:
    ::

        reset_to_pending([user = None, notes = ''])

#. moderate (to use when status is available during runtime only):
    ::

        moderate(status, [user = None, notes = ''])

**An example usage** ::

    >>> my_inst = MyModel.objects.create(arg1 = 1)
    >>> my_inst.approve()

In addition, there are 3 public boolean properties also to let you know which
moderation status a particular object is in.

#. ``is_approved``

#. ``is_challenged``

#. ``is_pending``

**An example usage** ::

    >>> my_inst = MyModel.objects.create()
    >>> # Will be in pending status by default.
    >>> my_inst.is_approved
    ... False
    >>> my_inst.is_pending
    ... True
    >>> my_inst.approve()
    >>> my_inst.is_approved
    ... True

Post-moderation hook
=====================

If you want to perform something after an object is moderated, you can make use
of the ``post_moderation`` signal as in the below **example**: ::

    from django_monitor import post_moderation

    # handler_func: function to handle your post moderation activities.
    def handler_func(sender, instance, **kwargs):
        # sender: MyModel
        # instance: my_model instance that was just moderated
        pass

    # MyModel: The model whose moderation you are watching.
    class MyModel(models.Model):
        pass

    post_moderation.connect(handler_func, sender = MyModel)

Note that the moderated object will be passed as the ``instance`` and its model
as the ``sender``. This will help you to write separate handlers for each model.

