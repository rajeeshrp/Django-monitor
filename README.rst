===============
Django-monitor
===============

---------------------------------------------------------
A django-app to enable moderation of model objects
---------------------------------------------------------

Expected work-flow:
===================

Registration
-------------
A developer can register models for moderation. A register hook will
be provided to accept the model along with some other arguments.

Permission
-----------
During database syncing, a basic permission, ``moderate_model`` will be
created for each model registered for moderation.

.. note::

The users who have add/edit permissions will be called non-managers and
those who have moderate permission also (in addition to add/edit) will
be called managers from now onwards.

Auto-moderation
----------------
#. When a non-manager creates an object that belongs to a moderated model,
   it will have a pending status. (status = ``In Pending``). Each of these
   objects can later be approved or challenged by a manager.

#. When a manager creates an object that belongs to a moderated model,
   it will get approved automatically (status = ``Approved``).

Moderation-lists
----------------
When a manager logs into the admin-site, he can see two links, ``n Pending``
and ``n Challenged``, in the rows of all moderated models which have objects
in the respective status. ``n`` is the number of objects to be moderated.
On clicking the link, manager can see the change-list of all such objects.

Moderation actions
-------------------
Change-list of each moderated model contains three actions, ``approve``,
``challenge`` and ``reset to pending``. If the manager selects few objects,
choose the action ``approve`` and press ``Go``, those objects will get
approved. Similarly, one can challenge some objects too. Once some objects
get challenged, the non-managers with edit permissions may check them
again and make required corrections. After that, they can reset the status to
``In pending`` so that their manager gets to verify them again.

Related moderation
-------------------
When a manager moderates some model objects, there may be some other related
model objects which also can get moderated along with the original ones. The
developer can specify such related models to be moderated during registration.

Locks
------
The developer can protect the approved objects from further modification and
deletion to maintain data integrity. The fields which are not meant to be
changed after approval can be specified in the model-admin using
``protected_fields`` option. The model-admin will club them with readonly_fields
if the object is approved. Similarly, developer can block deletion also.


