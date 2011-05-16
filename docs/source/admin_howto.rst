
.. _`admin_howto`:

=============================
How to use (for admin-users)
=============================

All moderation activities can be performed from within the admin changelist
itself. The changelist view of a moderated model will look like that in the
screen-shot below :

.. image:: _static/custom_changelist.jpg
   :scale: 70
   :alt: Change-list

Who can moderate
==================

Django-monitor creates a moderate permission for each moderated model. Only
those users with required permission can moderate any object of a particular
model. The superuser must assign those permissions to the appropriate users
as they would do with other commonly found permissions.

What to moderate & from where
===============================

To see and moderate the pending/challenged objects of a particualr model, visit
the change-list page of that model. By default, all existing objects appear
there. For moderated models, we add one more column, ``status`` to the right of
each row. That column, as its name indicates, displays the current moderation
status of each object you see in the list. This helps you to identify the
pending as well as challenged objects. Also, you can filter the objects by their
``moderation status`` using the filter options provided in the box to the right
of change-list. Refer to the screen-shot given above.

You need not regularly visit change-lists of all models to know whether there
are any objects to be moderated. ``Moderation Queue`` is the shortcut for this.
It will summarize the moderation status for all models in one page. Click on
the ``Moderation Queue`` change-link under the ``Monitor`` app in your admin
home page. You can see the number of pending and challenged objects for each
moderated model arranged in a nice table in the resulting page. Clicking on
each number will lead you to the corresponding change-list filtered by the
respective status. eg, if you clicked on the number of pending objects of the
model, say, `Book`, the change-list showing all pending book objects will be
loaded.

How to moderate
=================

Moderation is performed through 3 special change-list actions. They are,
``Approve selected``, ``Challenge selected`` and ``Reset selected to pending``.
If the manager selects few objects, choose the action ``Approve selected`` and
press ``Go``, those objects will get approved. Similarly, one can challenge some
objects too. Once some objects get challenged, the non-managers may check them
again and make required corrections. After that, they can reset the status to
``In pending`` using the action, ``Reset selected to pending`` so that their
manager gets to verify the entries again.

