from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'kittylover123',
            'password': 'i_secretly_hate_kitties'
        }
        User.objects.create_user(**self.credentials)

    def test_login_user(self):
        client_reg = Client()
        client_reg.post(path='/users/register_user', data=
        {
            "username": "BabbitNotRabbit",
            "email": "nevanmasterson1@gmail.com",
            "password1": "password1(verysecure)",
            "password2": "password1(verysecure)"
        })

        client_log = Client()
        response_login = client_log.post(path='/users/login_user', data=
        {
            "username": "BabbitNotRabbit",
            "password": "password1(verysecure)"
        }, follow=True)
        # Can only access kitty if the user is authenticated properly, so context is not authenticated if follow=False

        # self.assertEqual(response_login.url, '/climate')
        self.assertEqual(response_login.context['user'].is_authenticated, True)
        self.assertEqual(response_login.status_code, 200)


    def test_create_user(self):
        client = Client()
        response = client.post(path='/users/register_user', data=
        {
            "username": "BabbitNotRabbit",
            "email": "nevanmasterson1@gmail.com",
            "password1": "password1(verysecure)",
            "password2": "password1(verysecure)"
        })
        print(response)
        get = User.objects.get(username='BabbitNotRabbit')

        if get is None:
            self.fail()

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
    '''
