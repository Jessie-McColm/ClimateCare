from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from climate.models import Creature, Profile, LocationFountain, LocationBin, Advice
from django.test import Client
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta


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
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.status_code, 302)
        #should ask lucia why this happens
        self.assertEqual(response.url,"/users/login_user?next=/climate/kitty")
        

    def test_authorised_user(self):
        #test if a given user returns a page with the correct data
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

        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/kitty')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_post_articles(self):
        #test if valid response if given when a post request is sent to get articles/feed the kitty
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
        new_advice = Advice(content="example advice", source ="example")
        new_advice.save()
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"feed"})
        self.assertEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_not_articles(self):
        #test if valid response if given when a post request is sent to get articles/feed the kitty
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
        location = LocationFountain(longitude=0, latitude=0)
        location.save()

        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        self.assertNotEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_water(self):
        #test if valid response if given when a post request is sent to water the kitty
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
        location = LocationFountain(longitude=0, latitude=0)
        location.save()
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        self.assertEqual(response.context['task'],"water")
        self.assertEqual(response.status_code, 200)

    def test_post_not_water(self):
        #test if valid response if given when a post request is sent to water the kitty
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
        location = LocationFountain(longitude=1000, latitude=1000)
        location.save()
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        self.assertNotEqual(response.context['task'],"water")
        self.assertEqual(response.status_code, 200)

    def test_post_clean(self):
        #test if valid response if given when a post request is sent to clean the kitty
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
        location = LocationBin(longitude=0, latitude=0)
        location.save()

        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        self.assertEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)

    def test_post_not_clean(self):
        #tests that sending a water task does not result in a clean task being performed
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
        location = LocationBin(longitude=10000, latitude=10000)
        location.save()
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        self.assertNotEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)
    
    def test_advice_creation(self):
        advice1 = Advice.objects.create(link="https://example.com", source="admin")
        advice2 = Advice.objects.create(content="this is some advice!", source="admin")
        self.assertEqual(len(list(Advice.objects.all())), 2)


    def test_advice_url(self):
        #testing if advice data is sent back correctly when a request is made to climate/kitty/articles 
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
        advice1 = Advice.objects.create(link="https://example.com", source="admin")
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/kitty/articles')
        self.assertEqual(response.context['fed'],True)
        self.assertNotEqual(response.context['message'],"")
        self.assertNotEqual(response.context['content'],"")
        self.assertNotEqual(response.context['source'],"")
        self.assertEqual(response.status_code, 200)

    def test_water_url(self):
        #testing if data saying the cat was watered is sent back correctly when a request is made to climate/kitty/water 
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
     
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/kitty/water')
        self.assertEqual(response.context['watered'],True)
        self.assertEqual(response.status_code, 200)

    def test_water_url(self):
        #testing if data saying the cat was cleaned is sent back correctly when a request is made to climate/kitty/clean 
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
       
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/kitty/clean')
        self.assertEqual(response.context['cleaned'],True)
        self.assertEqual(response.status_code, 200)

    def test_stinky_cat_is_stinky(self):
        #sets up a creature object that has not been cleaned in over 3 days, so should be judged as "stinky"
        currentTime = timezone.now()
        pastTime=currentTime-timedelta(days=5)
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username='kittylover123')
     
        user_prof = Profile.objects.get(user=user_obj)
        cat_data = user_prof.creature
        cat_data.last_litter_refill = pastTime  
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['stinky'],True)
        self.assertEqual(response.status_code, 200)
        
    def test_clean_cat_is_clean(self):
        #sets up a creature object that has been cleaned recently, so should not be judged as "stinky"
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
      
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['stinky'],False)
        self.assertEqual(response.status_code, 200)

    def test_thirsty_cat_is_thirsty(self):
        #sets up a creature object that has not been watered in over 3 days, so should be judged as "thirsty"
        currentTime = timezone.now()
        pastTime=currentTime-timedelta(days=9)
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username='kittylover123')
     
        user_prof = Profile.objects.get(user=user_obj)
        cat_data = user_prof.creature
        cat_data.last_thirst_refill = pastTime  
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['thirsty'],True)
        self.assertEqual(response.status_code, 200)

    def test_non_thirsty_cat_is_not_thirsty(self):
        #sets up a creature object that has been watered recently, so should not be judged as "thirsty"
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['thirsty'],False)
        self.assertEqual(response.status_code, 200)
        
    def test_hungry_cat_is_hungry(self):
        #sets up a creature object that has not been fed in over 3 days, so should be judged as "hungry"
        currentTime = timezone.now()
        pastTime=currentTime-timedelta(days=5)
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username='kittylover123')
     
        user_prof = Profile.objects.get(user=user_obj)
        cat_data = user_prof.creature
        cat_data.last_food_refill = pastTime  
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['hungry'],True)
        self.assertEqual(response.status_code, 200)
        
    def test_fed_cat_is_fed(self):
        #sets up a creature object that has been watered recently, so should not be judged as "thirsty"
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/kitty')
        self.assertEqual(response.context['hungry'],False)
        self.assertEqual(response.status_code, 200)
        

class GeoLocationTests(TestCase):
    
    def test_within_dist(self):
        loc1=(28.426846,77.088834)
        loc2=(28.394231,77.050308)

        self.assertFalse(within_distance(loc1, loc2, 10))
        self.assertTrue(within_distance(loc1, loc2, 6000))
