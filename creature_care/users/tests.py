from django.test import TestCase
from django.urls import reverse
from django.test import Client

class LoginViewTests(TestCase):

    def test_login_user(self):
        client = Client()
        response = client.post(path='/users/login_user', data={
            "username":"BabbitRabbit", "password":"password1(verysecure)"
        }, follow=True)
        response.
        self.assertTrue(response.context['user'].is_authenticated)
        # self.assertEqual(response.url, '/climate/kitty')
        # self.assertEqual(response.status_code, 302)
        del client

    def test_invalid_username(self):
        client = Client()
        response = client.post(path='/users/login_user', data={
            "username":"BabbitNotRabbit","password":"password0(verynotsecure)"
        })
        self.assertEqual(response.url, "/users/login_user")
        self.assertEqual(response.status_code, 302)
        del client

