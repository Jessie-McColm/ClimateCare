from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User


class LoginViewTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'kittylover123',
            'password': 'i_secretly_hate_kitties'
        }
        User.objects.create_user(**self.credentials)

    def test_login_user(self):



        response = self.client.post('/users/login_user', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

        '''
        response = client.post(path='/users/login_user', data={
            "username":"BabbitRabbit", "password":"password1(verysecure)"
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.url, '/climate/kitty')
        self.assertEqual(response.status_code, 302)
        del client
        '''

    def test_invalid_username(self):
        client = Client()
        client.login()
        response = client.post(path='/users/login_user', data={
            "username":"BabbitNotRabbit","password":"password0(verynotsecure)"
        })
        self.assertEqual(response.url, "/users/login_user")
        self.assertEqual(response.status_code, 302)
        del client

