
.. _`intro`:

===============================
Introduction to Django-monitor
===============================

.. note::
   You can skip this chapter if you have already read the README document in
   source path.

About
=====

Moderation seems to be some job each one want to do in their own way.
Django-monitor is a django-app to moderate model objects. It was started as
a clone of the `django-gatekeeper` project but to meet a different set of
business requirements.

*The terms, ``monitor`` and ``moderate`` are used with same meaning everywhere
in the source.*

Here, the moderation process is well integrated with django-admin. That is,
all moderation actvities are performed from within the changelist page itself.

Installation
=============

#. Directly from the python package index

   #. Using pip: ::

        $ pip install django_monitor

   #. Using easy_install: ::

        $ easy_install django_monitor

#. OR Directly from the mercurial repo

    #. Clone the repo (if you have hg installed): ::

        $ hg clone http://bitbucket.org/rajeesh/django-monitor/

#. OR Download & install from available archives

   * Get the archive from any of the following locations:

     + http://bitbucket.org/rajeesh/django-monitor/downloads

     + http://pypi.python.org/pypi/django-monitor#downloads

   * Install using the setuptools as given below: ::

        $ tar xzf django-monitor-xxx.tar.gz
        $ cd django-monitor-xxx
        $ python setup.py install

   * If setuptools is not installed, you may copy the ``django_monitor``
     directory to somewhere in your python path.

#. Then add 'django_monitor' to your project's ``settings.INSTALLED_APPS``.

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

