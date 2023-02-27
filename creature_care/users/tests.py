from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist


class LoginViewTests(TestCase):

    def test_create_user(self):
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')

        self.assertIsNotNone(user)

    def test_login_user(self):
        client_reg = Client()
        g1 = Group.objects.create(name='Player')
        client_reg.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')

        client_log = Client()
        response_login = client_log.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        }, follow=True)
        # Can only access kitty if the user is authenticated properly, so context is not authenticated if follow=False

        self.assertIsNotNone(user)
        self.assertTrue(response_login.context['user'].is_authenticated)
        self.assertEqual(response_login.status_code, 200)

    def test_invalid_password(self):
        g1 = Group.objects.create(name='Player')
        client_reg = Client()
        client_reg.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client_login = Client()
        client_login.login()
        response_not_follow = client_login.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "obviously_i_love_kitties"
        })
        response_follow = client_login.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "obviously_i_love_kitties"
        }, follow=True)

        self.assertFalse(response_follow.context['user'].is_authenticated)
        self.assertEqual(response_not_follow.url, "/users/login_user")
        self.assertEqual(response_not_follow.status_code, 302)

    def test_blank_credentials(self):
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.login()
        response_not_follow = client.post(path='/users/login_user', data={
            "username": "",
            "password": ""
        })
        response_follow = client.post(path='/users/login_user', data={
            "username": "",
            "password": ""
        }, follow=True)

        self.assertFalse(response_follow.context['user'].is_authenticated)
        self.assertEqual(response_not_follow.url, "/users/login_user")
        self.assertEqual(response_not_follow.status_code, 302)

    def test_various_chars_in_username(self):
        client = Client()
        g1 = Group.objects.create(name='Player')
        response = client.post(path='/users/register_user', data={
            "username": "!\"#$%&'()*+,-./0123456789:;<=>?@¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿",
            "email": "strange@characters.com",
            "password1": "i_love_unicode",
            "password2": "i_love_unicode"
        })

        try:
            User.objects.get(username="!\"#$%&'()*+,-./0123456789:;<=>?@¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿")
            self.fail()  # if this statement is reached, it means that the user account was created. can't have that!
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, 200)  # ensures that the user hasn't been redirected

    def test_mismatching_passwords(self):
        client = Client()
        g1 = Group.objects.create(name='Player')
        response = client.post(path='/users/register_user', data={
            "username": "schroedingerskitty",
            "email": "schroedingerskitty@deadoralive.com",
            "password1": "the_kitty_is_dead",
            "password2": "the_kitty_is_alive"
        })

        try:
            User.objects.get(username='kittylover123')
            self.fail()
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, 200)
