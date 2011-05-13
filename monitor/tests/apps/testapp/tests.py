import re
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from monitor.conf import PENDING_STATUS, CHALLENGED_STATUS, APPROVED_STATUS

from monitor.tests.utils.testsettingsmanager import SettingsTestCase
from monitor.tests.apps.testapp.models import Author, Book, Supplement, Publisher

def get_perm(Model, perm):
    """Return the permission object, for the Model"""
    ct = ContentType.objects.get_for_model(Model)
    return Permission.objects.get(content_type = ct, codename = perm)

def moderate_perm_exists(Model):
    """ Returns whether moderate permission exists for the given model or not."""
    ct = ContentType.objects.get_for_model(Model)
    return Permission.objects.filter(
        content_type = ct,
        codename = 'moderate_%s' % Model._meta.object_name.lower()
    ).exists()

class ModPermTest(SettingsTestCase):
    """ Make sure that moderate permissions are created for required models."""
    test_settings = 'monitor.tests.settings'

    def test_perms_for_author(self):
        """ Testing moderate_perm exists for Author..."""
        self.assertEquals(moderate_perm_exists(Author), True)

    def test_perms_for_book(self):
        """ Testing moderate_ perm exists for Book """
        self.assertEquals(moderate_perm_exists(Book), True)

    def test_perms_for_supplement(self):
        """ Testing moderate_ perm exists for Supplement """
        self.assertEquals(moderate_perm_exists(Supplement), True)

    def test_perms_for_publisher(self):
        """ Testing moderate_ perm exists for Publisher """
        self.assertEquals(moderate_perm_exists(Publisher), False)

class ModTest(SettingsTestCase):
    """ Testing Moderation facility """
    fixtures = ['test_monitor.json']
    test_settings = 'monitor.tests.settings'

    def get_csrf_token(self, url):
        """ Scrape CSRF token """
        response = self.client.get(url, follow = True)
        csrf_regex = r'csrfmiddlewaretoken\'\s+value=\'([^\']+)\''
        return re.search(csrf_regex, response.content).groups()[0]
    
    def setUp(self):
        """ Two users, adder & moderator. """
        # Permissions
        add_auth_perm = get_perm(Author, 'add_author')
        mod_auth_perm = get_perm(Author, 'moderate_author')
        add_bk_perm = get_perm(Book, 'add_book')
        mod_bk_perm = get_perm(Book, 'moderate_book')
        add_sup_perm = get_perm(Supplement, 'add_supplement')
        mod_sup_perm = get_perm(Supplement, 'moderate_supplement')
        ch_auth_perm = get_perm(Author, 'change_author')
        ch_bk_perm = get_perm(Book, 'change_book')

        self.adder = User.objects.create_user(
            username = 'adder', email = 'adder@monitor.com',
            password = 'adder'
        )
        self.adder.user_permissions = [
            add_auth_perm, add_bk_perm, add_sup_perm, ch_auth_perm
        ]
        self.adder.is_staff = True
        self.adder.save()
        self.moderator = User.objects.create_user(
            username = 'moder', email = 'moder@monitor.com',
            password = 'moder'
        )
        self.moderator.user_permissions = [
            add_auth_perm, add_bk_perm, add_sup_perm,
            mod_auth_perm, mod_bk_perm, mod_sup_perm,
            ch_auth_perm, ch_bk_perm
        ]
        self.moderator.is_staff = True
        self.moderator.save()

    def tearDown(self):
        self.adder.delete()
        self.moderator.delete()

    def test_moderation(self):
        """ 
        Adder has permission to add only. All objects he creates are in Pending.
        Moderator has permissions to add & moderate also. All objects he creates
        are auto-approved.
        """
        # adder logs in. 
        logged_in = self.client.login(username = 'adder', password='adder')
        self.assertEquals(logged_in, True)
        # Make sure that no objects are there 
        self.assertEquals(Author.objects.count(), 0) 
        self.assertEquals(Book.objects.count(), 0)
        self.assertEquals(Supplement.objects.count(), 0)
        # Adding 2 Author instances...
        url = '/admin/testapp/author/add/'
        # Author 1
        data = {'age': 34, 'name': "Adrian Holovaty"}
        response = self.client.post(url, data, follow = True)
        # Author 2
        data = {'age': 35, 'name': 'Jacob kaplan-Moss'}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        # 2 Author instances added. Both are in pending (IP)
        self.assertEquals(Author.objects.count(), 2)
        self.assertEquals(Author.objects.get(pk=1).status, PENDING_STATUS)
        self.assertEquals(Author.objects.get(pk=2).status, PENDING_STATUS)
        # Adding 1 book instance...
        url = '/admin/testapp/book/add/'
        data = {
            'publisher': 1, 'isbn': '159059725', 'name': 'Definitive', 
            'authors': [1, 2], 'pages': 447
        }
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        # 1 Book instance added. In pending (IP)
        self.assertEquals(Book.objects.count(), 1)
        self.assertEquals(Book.objects.get(pk=1).status, PENDING_STATUS)
        # Adding 2 Supplement instances
        url = '/admin/testapp/supplement/add/'
        data = {'serial_num': 1, 'book': 1}
        response = self.client.post(url, data, follow = True)
        data = {'serial_num':2, 'book':1}
        response = self.client.post(url, data, follow = True)
        # 2 Supplement instances added. In Pending (IP)
        self.assertEquals(Supplement.objects.count(), 2)
        self.assertEquals(Supplement.objects.get(pk=1).status, PENDING_STATUS)
        self.assertEquals(Supplement.objects.get(pk=2).status, PENDING_STATUS)

        # Adder logs out
        self.client.logout()
    
        # moderator logs in. 
        logged_in = self.client.login(username = 'moder', password = 'moder')
        self.assertEquals(logged_in, True)
        # Adding one more author instance...
        url = '/admin/testapp/author/add/'
        # Author 3
        data = {'age': 46, 'name': "Stuart Russel"}
        response = self.client.post(url, data, follow = True)
        # Author 3 added. Auto-Approved (AP)
        self.assertEquals(Author.objects.count(), 3)
        self.assertEquals(Author.objects.get(pk=3).status, 'AP')
        # Approve Author 1 (created by adder)
        url = '/admin/testapp/author/'
        data = {'action': 'approve_selected', 'index': 0, '_selected_action': 1}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Author.objects.get(pk=1).status, APPROVED_STATUS)
        # Challenge Author 2 (created by adder)
        data = {'action': 'challenge_selected', 'index': 0, '_selected_action': 2}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Author.objects.get(pk=2).status, CHALLENGED_STATUS)
        # Approve Book 1 (created by adder). Supplements also get approved.
        url = '/admin/testapp/book/'
        data = {'action': 'approve_selected', 'index': 0, '_selected_action': 1}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Book.objects.get(pk=1).status, APPROVED_STATUS)
        self.assertEquals(Supplement.objects.get(pk=1).status, APPROVED_STATUS)
        self.assertEquals(Supplement.objects.get(pk=2).status, APPROVED_STATUS)

        # moderator logs out
        self.client.logout()
        # adder logs in again
        logged_in = self.client.login(username = 'adder', password = 'adder')
        self.assertEquals(logged_in, True)

        # Edit the challenged Author, author 2.
        self.failUnlessEqual(Author.objects.get(pk=2).age, 35)
        url = '/admin/testapp/author/2/'
        data = {'id': 2, 'age': 53, 'name': 'Stuart Russel'}
        response = self.client.post(url, data)
        self.assertRedirects(response, '/admin/testapp/author/', target_status_code = 200)
        self.failUnlessEqual(Author.objects.get(pk=2).age, 53)
        # Reset Author 2 back to pending
        url = '/admin/testapp/author/'
        data = {'action': 'reset_to_pending', 'index': 0, '_selected_action': 2}
        response = self.client.post(url, data, follow = True)
        self.failUnlessEqual(Author.objects.get(pk=2).status, PENDING_STATUS)

