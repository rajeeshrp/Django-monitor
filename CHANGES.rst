==========================
Django-monitor: CHANGE LOG
==========================

0.1.4
======

* Now we have finished implementation of one more TODO things: A single place
  to manage monitored objects. The model change-link, ``Moderation Queue``,
  under the app, ``Monitor`` in admin-home page leads user to a page listing
  the counts of pending/challenged objects for each monitored models.

* ERROR_FIX: In ``monitor.admin.has_delete_permission``, we tried to retrieve
  the model class as ``self.opts.model``. It should be ``self.model``. Fixed.

0.1.3
======

* Now developers can block admin-users from deleting approved objects of
  desired models. An additional parameter, ``can_delete_approved``, is added
  to ``monitor.nq`` to enable this. Default value is ``True``.

0.1.2
=====

* Django-monitor now generates a ``post_moderation`` signal whenever an object
  is moderated. Developers can make use of this if they want to invoke some
  function right after moderation. See ``docs/dev_howto.rst`` for details.

0.1.1
======

* monitor now contains one more utility function, ``get_monitor_entry``.
  It will return the monitor_entry that corresponds to the given object.
  **Example**: ::

    import monitor
    monitor.get_monitor_entry(model_obj)

* The model, ``MonitorEntry`` now supports the following public methods to
  help developer:

  + ``approve``, ``challenge`` and ``reset_to_pending`` to moderate objects
    by code.  Combining with get_monitor_entry, a developer may write: ::

      import monitor
      my_inst = MyModel.objects.create(arg1 = 1)
      # my_inst is in pending status now.
      monitor.get_monitor_entry(my_inst).approve()
      # Now it got approved.

  + ``moderate`` does the same job as above but can be used when the moderation
    status is not known but stored in some variable. ::

      # We want to set status of my_inst to the value stored in say, `status`.
      monitor.get_monitor_entry(my_inst).moderate(status)

  + ``is_approved``, ``is_challenged`` and ``is_pending`` can be used to make
      sure that the desired object is in some particular moderation status. ::

        monitor.get_monitor_entry(my_inst).is_approved()

* BUGFIX: There was a bug with our ``save_handler`` function which handled the
  post_save moderation. Whenever an object is saved, the function would invoke
  ``moderate_rel_objects`` which in turn reset status of the objects and all of
  its related objects to PENDING_STATUS. ``moderate_rel_objects`` should be
  invoked here for newly created objects only. Fixed.

* The documentation is updated to inlcude new changes in code.

