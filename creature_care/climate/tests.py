from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from climate.models import Creature, Profile, LocationFountain, LocationBin
from django.test import Client
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from .views import within_distance

class UserModelTests(TestCase):

    def test_create_user(self):
        #i guess test if various DB functions work?
        testUser = User.objects.create_user('testUser', 'test@test.com', 'testPass')
        check= User.objects.get(username = "testUser")
        self.assertIs(True,check==testUser)
        testUser.delete()

    def test_create_profile(self):
        testUser = User.objects.create_user('testUser', 'test@test.com', 'testPass')
        testKitty = Creature()
        testProfile = Profile(user=testUser, creature=testKitty)
        testKitty.save()
        testProfile.save()
        userObj = User.objects.get(username = "testUser")
        userProf=Profile.objects.get(user = userObj)
        self.assertIs(True,userProf==testProfile)
        self.assertIs(True,testKitty==userProf.creature)
        testProfile.delete()
        testKitty.delete()
        testUser.delete()


class KittyIndexTests(TestCase):
    #class to check that the data returned from the kitty view is correct

    def test_unauthorised_user(self):
        client=Client()
        response=client.get(path='/climate/')
        self.assertEqual(response.status_code, 302)
        #should ask lucia why this happens
        self.assertEqual(response.url,"/users/login_user?next=/climate/")
        

    def test_authorised_user(self):
        #test if a given user returns a page with the correct data
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')

        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_post_articles(self):
        #test if valid response if given when a post request is sent to get articles/feed the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')

        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"feed"})
        self.assertEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_not_articles(self):
        #test if valid response if given when a post request is sent to get articles/feed the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')

        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"water"})
        self.assertNotEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_water(self):
        #test if valid response if given when a post request is sent to water the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')
        location = LocationFountain(longitude=0, latitude=0)
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"water"})
        self.assertEqual(response.context['task'],"water")
        self.assertEqual(response.status_code, 200)

    def test_post_not_water(self):
        #test if valid response if given when a post request is sent to water the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')
        location = LocationFountain(longitude=10000, latitude=10000)
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"litter"})
        self.assertNotEqual(response.context['task'],"water")
        self.assertEqual(response.status_code, 200)

    def test_post_clean(self):
        #test if valid response if given when a post request is sent to clean the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')
        location = LocationBin(longitude=0, latitude=0)
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"litter"})
        self.assertEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)

    def test_post_not_clean(self):
        #test if valid response if given when a post request is sent to clean the kitty
        client = Client()
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user = User.objects.get(username='kittylover123')
        location = LocationBin(longitude=10000, latitude=10000)
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/', data=
                             {"coordinates":[0,0],
                              "task":"water"})
        self.assertNotEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)



class GeoLocationTests(TestCase):
    
    def test_within_dist(self):
        loc1=(28.426846,77.088834)
        loc2=(28.394231,77.050308)

        self.assertFalse(within_distance(loc1, loc2, 10))
        self.assertTrue(within_distance(loc1, loc2, 6000))