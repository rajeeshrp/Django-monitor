from django_monitor.tests.utils.testsettingsmanager import get_only_settings_locals

DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django_monitor',
    'django_monitor.tests.apps.testapp',
)

SERIALIZATION_MODULES = {}

ROOT_URLCONF = 'django_monitor.tests.urls'

settings = get_only_settings_locals(locals().copy())
