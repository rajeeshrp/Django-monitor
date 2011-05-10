from django.contrib import admin

from monitor.tests.apps.testapp.models import Author, Book, Supplement
from monitor.admin import MonitorAdmin

class AuthorAdmin(MonitorAdmin):
    pass

class BookAdmin(MonitorAdmin):
    pass

class SupAdmin(MonitorAdmin):
    pass

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Supplement, SupAdmin)

