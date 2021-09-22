from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import User, Reader, Librarian, Book


def create_test_user_and_group():
    reader_group = Group.objects.create(name=settings.READER_GROUP)
    librarian_group = Group.objects.create(name=settings.LIBRARIAN_GROUP)

    alice = User.objects.create_user('alice', 'alice@example.com', '1234')
    alice.groups.add(librarian_group)
    Librarian.objects.create(user=alice)
    bob = User.objects.create_user('bob', 'bob@example.com', '1234')
    bob.groups.add(reader_group)
    Reader.objects.create(user=bob)
    User.objects.create_user('guest', 'guest@example.com', '1234')


class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()

    def test_can_login(self):
        tests = [
            ('alice', False, True, True),
            ('bob', True, False, True),
            ('guest', False, False, False)
        ]
        for username, is_reader, is_librarian, can_login in tests:
            user = User.objects.get(username=username)
            self.assertEqual(is_reader, user.is_reader())
            self.assertEqual(is_librarian, user.is_librarian())
            self.assertEqual(can_login, user.can_login())


class LoginViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()

    def test_get(self):
        response = self.client.get(reverse('library:login'))
        self.assertTemplateUsed(response, 'library/account/login.html')

    def test_get_already_login(self):
        self.client.post(reverse('library:login'), data={'username': 'alice', 'password': '1234'})
        response = self.client.get(reverse('library:login'))
        self.assertRedirects(response, reverse('library:index'))

    def test_ok(self):
        data = {'username': 'bob', 'password': '1234'}
        response = self.client.post(reverse('library:login'), data)
        self.assertEqual('2', self.client.session[SESSION_KEY])
        self.assertRedirects(response, reverse('library:index'))

    def test_redirect(self):
        redirect_url = reverse('library:search-book') + '?title=xxx'
        login_url = '{}?next={}'.format(reverse('library:login'), quote(redirect_url))
        response = self.client.get(login_url)
        self.assertContains(response, 'action="{}"'.format(login_url))

        data = {'username': 'bob', 'password': '1234'}
        response = self.client.post(login_url, data)
        self.assertRedirects(response, redirect_url)

    def test_wrong_username_or_password(self):
        data = {'username': 'bob', 'password': '5678'}
        response = self.client.post(reverse('library:login'), data)
        self.assertTemplateUsed(response, 'library/account/login.html')
        self.assertContains(response, '用户名或密码错误')


class RegisterViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()

    def test_get(self):
        response = self.client.get(reverse('library:register'))
        self.assertTemplateUsed(response, 'library/account/register.html')

    def test_invalid_username(self):
        data = {'username': '@#%', 'password': '1234', 'password2': '1234'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('用户名只能包含字母、数字和下划线', response.context['message'])

    def test_username_already_exists(self):
        data = {'username': 'alice', 'password': '1234', 'password2': '1234'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('用户名已存在', response.context['message'])

    def test_passwords_not_match(self):
        data = {'username': 'cindy', 'password': '1234', 'password2': '5678'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('两次密码不一致', response.context['message'])

    def test_ok(self):
        data = {'username': 'cindy', 'password': '1234', 'password2': '1234', 'name': '', 'email': ''}
        response = self.client.post(reverse('library:register'), data)
        self.assertRedirects(response, reverse('library:login'))
        cindy = User.objects.get(username='cindy')
        self.assertTrue(cindy.is_reader())
        self.assertFalse(cindy.is_librarian())
        self.assertTrue(Reader.objects.filter(user=cindy).exists())


def create_test_books():
    Book.objects.create(title='The Adventures of Tom Sawyer', author='Mark Twain')
    Book.objects.create(title='The Adventures of Huckleberry Finn', author='Mark Twain')
    Book.objects.create(title="Gulliver's Travels", author='Jonathan Swift')


class SearchBookViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()
        create_test_books()

    def setUp(self):
        self.client.post(reverse('library:login'), data={'username': 'bob', 'password': '1234'})

    def test_search_book(self):
        response = self.client.get(reverse('library:search-book'), {'title': 'adventures'})
        self.assertEqual(200, response.status_code)
        expected = ['<Book: The Adventures of Tom Sawyer>', '<Book: The Adventures of Huckleberry Finn>']
        self.assertQuerysetEqual(response.context['book_list'], expected, ordered=False)

    def test_no_result(self):
        response = self.client.get(reverse('library:search-book'), {'title': 'xxx'})
        self.assertContains(response, '没有符合条件的图书')
        self.assertQuerysetEqual(response.context['book_list'], [])

    def test_not_login(self):
        self.client.get(reverse('library:logout'))
        response = self.client.get(reverse('library:search-book'), {'title': 'xxx'})
        self.assertRedirects(response, '{}?next={}'.format(
            reverse('library:login'), quote(reverse('library:search-book') + '?title=xxx')
        ))

    def test_not_login_as_reader(self):
        for username in ('alice', 'guest'):
            self.client.post(reverse('library:login'), data={'username': username, 'password': '1234'})
            response = self.client.get(reverse('library:search-book'), {'title': 'xxx'})
            self.assertEqual(403, response.status_code)


class BookDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()
        create_test_books()

    def setUp(self):
        self.client.post(reverse('library:login'), data={'username': 'bob', 'password': '1234'})

    def test_ok(self):
        book = Book.objects.get(pk=1)
        response = self.client.get(reverse('library:book-detail', args=(1,)))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, book.title)

    def test_not_found(self):
        response = self.client.get(reverse('library:book-detail', args=(999,)))
        self.assertEqual(404, response.status_code)
