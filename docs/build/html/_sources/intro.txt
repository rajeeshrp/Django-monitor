
.. _`intro`:

===============
Introduction
===============

About
=====

Moderation seems to be some job each one want to do in their own way.
Django-monitor is yet another django-app to help moderate model objects.
Other popular apps are Sunlight lab's `django-gatekeeper` and Dominno's
`django-moderation`. Our app is almost a clone of the `django-gatekeeper`
project but with some different features. The name ``monitor`` is just to
distinguish it from `django-moderation`. The terms, ``monitor`` and
``moderate`` are used with same meaning everywhere in the source code.

Here, any object created for a moderated model will have a moderation status
of  ``In Pending``, ``Challenged`` or ``Approved``. Each model has its own
``moderate_`` permission and only those users with corresponding permission
can moderate objects of that model. For any moderated model, three actions,
``approve_selected``, ``challenge_selected`` and ``reset_to_pending``, will
be available from among the change-list actions. Users can moderate objects
using these actions. Auto-moderation and related moderation are supported.
Also, you can protect approved objects from further editing or deletion.

Install
========

Grab the Source
---------------
* Download the latest version from bitbucket repo:
  http://bitbucket.org/rajeesh/django-monitor.
* Will be uploaded to pypi soon.

Place it in your path
----------------------
* Copy the ``monitor`` directory to some place in your python path.

Add to your project
--------------------
* Add to your django project by including it in settings.INSTALLED_APPS.

Features
=========

Permission
-----------
During database syncing, a basic permission, ``moderate_<model_name>`` will
be created for each model registered for moderation, where `<model_name>` is
replaced with the name of the corresponding model. eg, If you register your
`Book` model with monitor, there will be a permission, ``moderate_book``.
Only those users with that permission will be able to approve or challenge
any object created for that model.

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

Edit-Lock
----------
The developer can protect the approved objects from further modification to
maintain data integrity. The fields which are not meant to be changed after
approval can be specified in the model-admin using ``protected_fields`` option.
The model-admin will club them with readonly_fields if the object is approved.

TODO
======
* There should be a facility to lock deletion of approved objects too.

* When a manager logs into the admin-site, he should be able to see two links,
  ``n Pending`` and ``n Challenged``, in the rows of all moderated models
   with objects in the respective status. ``n`` is the number of objects to
   be moderated. On clicking the link, manager should be able to see the
   change-list of all such objects.

* The change-list should include a column, `status` for moderated models to
  display their current moderation status.

* The change-list filter should support status based filtering too for
  moderated models.

