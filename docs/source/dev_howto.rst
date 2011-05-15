
.. _`developers_howto`:

============================
How to use (for developers)
============================

Registration
============

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
  See the **example**:
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
    monitor.nq(Supplement)

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
==========================

As you might have noted from the above examples, we build admin classes for
moderated models using MonitorAdmin instead of django's built-in ModelAdmin.

::

  # in your admin.py
  from monitor.admin import MonitorAdmin
  class YourModelAdmin(MonitorAdmin):
      pass

Data-protection
================

``protected_fields`` in model-admin can be used to prevent users from
changing certain fields in approved objects. Specify the field names as you
do with ``readonly_fields``.::

  # in your admin.py
  class YourModelAdmin(MonitorAdmin):
      protected_fields = ['field1', 'field2']

Creation of objects by code
============================

The above sections shared tips on how to prepare your application for
moderation by admin-users. What about the objects you create by code? All
objects created by code will be in pending status by default. To moderate
such an object as you wish, get its associated monitor_entry using
``monitor.get_monitor_entry`` and then invoke applicable public method of it.
Available methods of monitor_entry are as follows:

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

    >>> import monitor
    >>> my_inst = MyModel.objects.create(arg1 = 1)
    >>> me = monitor.get_monitor_entry(my_inst)
    >>> me.approve()

To let you know which status a particular object is in, there are three more
methods with monitor_entry:

#. ``is_approved``

#. ``is_challenged``

#. ``is_pending``

**An example usage** ::

     >>> my_inst = MyModel.objects.create()
     >>> me = monitor.get_monitor_entry(my_inst)
     >>> # Will be in pending status by default.
     >>> me.is_approved()
     ... False
     >>> me.is_pending()
     ... True
     >>> me.approve()
     >>> me.is_approved()
     ... True

Post-moderation hook
=====================

If you want to perform something after an object is moderated, you can make use
of the ``post_moderation`` signal as in the below **example**: ::

    from monitor import post_moderation

    # handler_func: The function to handle your post moderation activities.
    def handler_func(sender, instance, **kwargs):
        # sender: MyModel
        # instance: my_model instance that was just moderated
        # do whatever you want..
        pass

    # MyModel: The model whose moderation you are watching.
    class MyModel(models.Model):
        pass

    post_moderation.connect(handler_func, sender = MyModel)

Note that the object moderated will be passed as the ``instance`` and its model
as the ``sender``. This will help you to write separate handlers for each model.

