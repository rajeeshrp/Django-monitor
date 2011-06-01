===============
Django-monitor
===============

---------------------------------------------------------
A django-app to enable moderation of model objects
---------------------------------------------------------

About
=====

Moderation seems to be some job each one want to do in their own way.
Django-monitor is a django-app to moderate model objects. It was started as
a clone of `django-gatekeeper` project but with some different set of
requirements.The name ``monitor`` is just to distinguish it from an existing
project, `django-moderation`. (The terms, ``monitor`` and ``moderate`` are used
with same meaning everywhere in the source.)

Here, the moderation process is well integrated with django-admin. That is, all
moderation actvities are performed from within the changelist page itself.

The detailed documentation is available at http://django-monitor.readthedocs.org/
and in the ``docs/`` directory inside the source path.

Installation
============

* Download the latest version from the bitbucket repo:
  http://bitbucket.org/rajeesh/django-monitor.

* Install using the setuptools as given below: ::

    $ python setup.py install

* Or copy the ``django_monitor`` directory to some place in your python path.

* Add 'django_monitor' to your project's ``settings.INSTALLED_APPS``.

Features
=========

Model-specific permission
--------------------------
Each moderated model will have an associated moderate permission. To approve
or challenge any object created for a particular model, users need to have
the corresponding permission.

Auto-moderation
----------------
Any object created by a user with add permission will have an ``In Pending``
status. If the user has got moderate permission also, the object created will
automatically get approved (status becomes ``Approved``).

Moderation from within admin changelist
----------------------------------------
The changelist of a moderated model displays the current moderation status of
all objects. Also, you can filter the objects by their moderation status. Three
actions are available for moderation. To moderate, user just need to select the
objects, choose appropriate action and press ``Go``.

Related moderation
-------------------
When a manager moderates some model objects, there may be some other related
model objects which also can get moderated along with the original ones. The
developer can specify such related models to be moderated during registration.

Data protection
----------------
The developer can prevent admin-users from changing values of selected fields
of approved objects. Deleting approved objects also can be prevented if your
client's business requires that.

Basic usage (developers)
========================

* Register the model for moderation using ``monitor.nq``.

  **Example**: ::

    import django_monitor
    from django.db import models
    class MyModel(models.Model):
        pass

    django_monitor.nq(MyModel)

* Inherit ``MonitorAdmin``, not ``ModelAdmin`` for moderated models. ::

    # in your admin.py
    from django_monitor.admin import MonitorAdmin
    class MyAdmin(MonitorAdmin):
        pass

    from django.contrib import admin
    admin.site.register(MyModel, MyAdmin)

More details at http://django-monitor.readthedocs.org. Or check the `docs/`
directory inside the source path, if you are working offline.

