#!/usr/bin/env python
import os
import sys

from django.conf import settings
try:
    from django.utils.functional import empty
except ImportError:
    empty = None

def setup_test_environment():
    """Reset settings to be just enough to test this app."""
    settings._wrapped = empty
    MIDDLEWARES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # We are concerned about this middleware only.
        'django_monitor.middleware.MonitorMiddleware',
    )
    apps = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.sites',
        'django_monitor',
        'django_monitor.tests.test_app',
    ]
    settings_dict = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test_dm.db'
            }
        },
        'MIDDLEWARE_CLASSES': MIDDLEWARES,
        'INSTALLED_APPS': apps,
        'STATIC_URL': '/static/',
        'ROOT_URLCONF': 'django_monitor.tests.urls'
    }
    settings.configure(**settings_dict)

def runtests(*test_args):
    """
    Build a test environment & a test_runner. Run the tests & return the 
    number of failures to terminal.
    """
    setup_test_environment()
    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    try:
        from django.test.simple import DjangoTestSuiteRunner

        def run_tests(test_args, verbosity, interactive):
            runner = DjangoTestSuiteRunner(
                verbosity = verbosity, interactive = interactive, 
                failfast = True
            )
            return runner.run_tests(test_args)
    except ImportError:
        from django.test.simple import run_tests

    failures = run_tests(test_args, verbosity = 1, interactive = True)
    sys.exit(failures)

if __name__ == "__main__":
    """Unit tests of the app, django_monitor, are run from here."""
    runtests('django_monitor')

