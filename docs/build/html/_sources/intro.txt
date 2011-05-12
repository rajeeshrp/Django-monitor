
.. _`intro`:

===============
Introduction
===============

About
=====

Moderation seems to be some job each one want to do in their own way.
Django-monitor is yet another django-app to help moderate model objects.
It was started by cloning the project `django-gatekeeper` but offers
different set of features. The name ``monitor`` is just to distinguish it
from the existing app, `django-moderation`. (The terms, ``monitor`` and
``moderate`` are used with same meaning everywhere in the source code.)

Here, the moderation process is well integrated with django-admin. That is,
all moderation actvities are performed from within the changelist page itself.

Install
========

Grab the Source
----------------
* Download the latest version from bitbucket repo:
  http://bitbucket.org/rajeesh/django-monitor.

Place it in your path
----------------------
* Copy the ``monitor`` directory to some place in your python path.

Add to your project
--------------------
* Add to your django project by including it in settings.INSTALLED_APPS.

Features
=========

Model-specific permission
--------------------------
Each moderated model will have an associated moderate permission of the form,
``moderate_<model_name>`` where `<model_name>` represents the name of the
model. Only those users with that permission will be able to approve or
challenge any object created for that model.

Auto-moderation
----------------
Any object created by a user with add permission will have an ``In Pending``
status. If the user has got moderate permission also, the object created will
automatically get approved (status is ``Approved``).

Moderation from within admin changelist
----------------------------------------
The changelist view displays an additional column showing current moderation
status of each object. Also, you can filter the changelist entries by their
moderation status. Three actions, ``approve``, ``challenge`` and
``reset to pending`` are provided for moderation. The user just need to select
the objects, choose appropriate action and press ``Go`` to moderate.

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

* There should be a notification area to show counts of pending as well as
  challenged objects for each moderated model. So user need not routinely check
  every changelist just to know if there exists entries to be moderated.

