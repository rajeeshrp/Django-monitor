from monitor.tests.utils.testsettingsmanager import get_only_settings_locals

DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'monitor',
    'monitor.tests.apps.testapp',
)

SERIALIZATION_MODULES = {}

ROOT_URLCONF = 'monitor.tests.urls'

settings = get_only_settings_locals(locals().copy())
