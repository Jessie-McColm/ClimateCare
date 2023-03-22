"""
The testing file for ClimateCare. This file can be run with `py manage.py test` and should pass all tests
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from climate.models import Creature, Profile, LocationFountain, LocationBin, Advice, Colour, Item, Wearing
from django.test import Client
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from time import sleep

from .views import within_distance

class UserModelTests(TestCase):

    """
    Block of tests for the climate view.

    Authors:
        Jessie, Laurie, Lucia, and Nevan
    """

    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )

    def test_create_user(self):
        """
        Tests that various database functions are operational from climate/view.

        Author:
            Jessie
        """
        test_user = User.objects.create_user('test_user', 'test@test.com', 'testPass')
        check = User.objects.get(username="test_user")
        self.assertIs(True, check == test_user)
        test_user.delete()

    def test_create_profile(self):
        """
        Tests that a Profile entrance can be created and linked to a user account

        Author:
            Jessie
        """
        test_user = User.objects.create_user('test_user', 'test@test.com', 'testPass')
        test_kitty = Creature()
        test_profile = Profile(user=test_user, creature=test_kitty)
        test_kitty.save()
        test_profile.save()
        user_obj = User.objects.get(username="test_user")
        user_prof = Profile.objects.get(user=user_obj)
        self.assertIs(True, user_prof == test_profile)
        self.assertIs(True, test_kitty == user_prof.creature)
        test_profile.delete()
        test_kitty.delete()
        test_user.delete()


class KittyIndexTests(TestCase):
    """
    Test to check that the data returned from the kitty view is correct

    Authors:
        Laurie and Jessie
    """

    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#2196f3",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )


    def test_unauthorised_user(self):
        """
        Test to check that a user that has not logged in is redirected to the login page
        when attempting to access the home page
        """
        client = Client()
        response = client.get(path='/climate/kitty')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login_user?next=/climate/kitty")
        

    def test_authorised_user(self):
        """
        Test if a given user returns a page with the correct data

        Authors:
            Jessie and Laurie
        """

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
        self.assertEqual(response.context['fur_colour'],'#000000,')
        self.assertEqual(response.context['eye_colour'],'#2196f3')
        self.assertEqual(response.status_code, 200)

    def test_post_articles(self):
        """
        Test if valid response is given when a post request is sent to get articles/feed the kitty

        Authors:
            Jessie and Laurie
        """
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
        user_prof = Profile.objects.get(user=user)
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_food_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response = client.post(path='/climate/kitty', data=
                             {"coordinates": "0,0",
                              "task": "feed"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 1)
        self.assertEqual(profile.num_times_fed, 1)
        self.assertEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_articles_when_paused(self):
        """
        Test if points aren't updated when user sends a request when paused

        Authors:
            Jessie 
        """
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
        user_prof = Profile.objects.get(user=user)
        user_prof.paused=True
        user_prof.save()
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_food_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response = client.post(path='/climate/kitty', data=
                             {"coordinates": "0,0",
                              "task": "feed"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.num_times_fed, 0)
        self.assertEqual(response.context['task'],"none")
        self.assertEqual(response.status_code, 200)


        
    def test_post_not_articles(self):
        """
        Test if valid response is given when a post request is sent to get articles/feed the kitty

        Author:
            Jessie and Laurie
        """
        client = Client()
        Group.objects.create(name='Player')
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
        user_prof = Profile.objects.get(user=user)
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_thirst_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response = client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 5)
        self.assertEqual(profile.num_times_fed, 0)
        self.assertNotEqual(response.context['task'],"feed")
        self.assertEqual(response.status_code, 200)

    def test_post_water(self):
        """
        Test if valid response is given when a post request is sent to water the kitty

        Author:
            Jessie and Laurie
        """
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
        user_prof = Profile.objects.get(user=user)
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_thirst_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response = client.post(path='/climate/kitty', data=
                             {
                                 "coordinates": "0,0",
                                 "task": "water"
                             })
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 5)
        self.assertEqual(profile.num_times_watered, 1)
        self.assertEqual(response.context['task'], "water")
        self.assertEqual(response.status_code, 200)
        
    def test_post_water_when_paused(self):
        """
        Test if points aren't updated when user sends a request when paused

        Author:
            Jessie  
        """
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
        user_prof = Profile.objects.get(user=user)
        user_prof.paused=True
        user_prof.save()
        
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_thirst_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response = client.post(path='/climate/kitty', data=
                             {
                                 "coordinates": "0,0",
                                 "task": "water"
                             })
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.num_times_watered, 0)
        self.assertEqual(response.context['task'], "none")
        self.assertEqual(response.status_code, 200)
    
    def test_post_not_water(self):
        """
        Test if valid response is given when a post request is sent to water the kitty

        Authors:
            Jessie and Laurie
        """
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
        user_prof = Profile.objects.get(user=user)
        user_prof.paused=True
        user_prof.save()

        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_thirst_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.num_times_watered, 0)
        self.assertNotEqual(response.context['task'],"water")
        self.assertEqual(response.status_code, 200)

    def test_post_clean(self):
        """
        Test if valid response is given when a post request is sent to clean the kitty

        Authors:
            Jessie and Laurie
        """
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
        user_prof = Profile.objects.get(user=user)
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_litter_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 3)
        self.assertEqual(profile.num_times_litter_cleared, 1)
        self.assertEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)

    def test_post_clean_when_paused(self):
        """
        Test if points aren't updated when user sends a request when paused

        Authors:
            Jessie 
        """
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
        user_prof = Profile.objects.get(user=user)
        user_prof.paused=True
        user_prof.save()
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_litter_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.num_times_litter_cleared, 0)
        self.assertEqual(response.context['task'],"none")
        self.assertEqual(response.status_code, 200)

    def test_post_not_clean(self):
        """
        Tests that sending a water task does not result in a clean task being performed

        Authors:
            Jessie and Laurie
        """
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
        user_prof = Profile.objects.get(user=user)
        cat_data = user_prof.creature
        past_time = timezone.now()-timedelta(days=5)
        setattr(cat_data, "last_litter_refill", past_time)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.points, 0)
        self.assertEqual(profile.num_times_litter_cleared, 0)
        self.assertNotEqual(response.context['task'],"clean")
        self.assertEqual(response.status_code, 200)
    
    def test_advice_creation(self):
        """
        Tests that advice can be created within the database.
        """
        advice1 = Advice.objects.create(link="https://example.com", source="admin")
        advice2 = Advice.objects.create(content="this is some advice!", source="admin")
        self.assertEqual(len(list(Advice.objects.all())), 2)

    def test_advice_url(self):
        """
        Testing if advice data is sent back correctly when a request is
        made to climate/kitty/articles

        Author:
            Jessie
        """
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
        response = client.get(path='/climate/kitty/articles')
        self.assertEqual(response.context['fed'],True)
        self.assertNotEqual(response.context['message'], "")
        self.assertNotEqual(response.context['content'], "")
        self.assertNotEqual(response.context['source'], "")
        self.assertEqual(response.status_code, 200)

    def test_water_url(self):
        """
        Testing if data saying the cat was watered is sent back correctly when a request is made
        to climate/kitty/water

        Authors:
            Jessie
        """
        client = Client
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
        response = client.get(path='/climate/kitty/water')
        self.assertEqual(response.context['watered'],True)
        self.assertEqual(response.status_code, 200)

    def test_water_url(self):
        """
        Testing if data saying the cat was cleaned is sent back correctly when a request is
        made to climate/kitty/clean

        Author:
            Jessie
        """
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
        client.post(
            path='/users/login_user', data=
            {
                "username": "kittylover123",
                "password": "i_secretly_hate_kitties"
            }
        )
        response = client.get(path='/climate/kitty/clean')
        self.assertEqual(response.context['cleaned'],True)
        self.assertEqual(response.status_code, 200)

    def test_stinky_cat_is_stinky(self):
        """
        Sets up a creature object that has not been cleaned in over 3 days, so should be judged as "stinky"

        Author:
            Jessie
        """
        current_time = timezone.now()
        past_time = current_time-timedelta(days=5)
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
        cat_data.last_litter_refill = past_time
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
        """
        Sets up a creature object that has been cleaned recently, so should not be judged as "stinky"

        Author:
            Jessie
        """
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
        response = client.get(path='/climate/kitty')
        self.assertEqual(response.context['stinky'],False)
        self.assertEqual(response.status_code, 200)

    def test_thirsty_cat_is_thirsty(self):
        """
        Sets up a creature object that has not been watered in over 
        3 days, so should be judged as "thirsty"

        Author:
            Jessie
        """

        current_time = timezone.now()
        past_time = current_time-timedelta(days=9)
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
        cat_data.last_thirst_refill = past_time
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response = client.get(path='/climate/kitty')
        self.assertEqual(response.context['thirsty'], True)
        self.assertEqual(response.status_code, 200)

    def test_non_thirsty_cat_is_not_thirsty(self):
        """
        Sets up a creature object that has been watered recently, 
        so should not be judged as "thirsty"

        Author:
            Jessie
        """
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
        response = client.get(path='/climate/kitty')
        self.assertEqual(response.context['thirsty'],False)
        self.assertEqual(response.status_code, 200)
        
    def test_hungry_cat_is_hungry(self):
        """
        Sets up a creature object that has not been fed in over 3 days, so should be judged as "hungry"

        Author:
            Jessie
        """
        current_time = timezone.now()
        past_time = current_time-timedelta(days=5)
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
        cat_data.last_food_refill = past_time
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response = client.get(path='/climate/kitty')
        self.assertEqual(response.context['hungry'],True)
        self.assertEqual(response.status_code, 200)
        
    def test_fed_cat_is_fed(self):
        """
        Sets up a creature object that has been watered recently, so should not be judged as "thirsty"

        Author:
            Jessie
        """
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

    def test_stats_page(self):
        """
        Checks that the stats page returns the correct amount of points

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.num_times_watered=27
        user_prof.num_times_fed=40
        user_prof.num_times_litter_cleared=13
        user_prof.save()
        
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        response=client.get(path='/climate/my_stats')
        self.assertEqual(response.context['username'],'kittylover123')
        self.assertEqual(response.context['bottle_num'],27)
        self.assertEqual(response.context['article_num'],40)
        self.assertEqual(response.context['recycle_num'],13)
        self.assertEqual(response.status_code, 200)

class GMTests(TestCase):
    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
    
    def test_access_GM_page(self):
        """
        Test that a GM user can access the GM page

        Authors:
            Jessie 
        """
        client = Client()
        g1 = Group.objects.create(name='Game_master')
        g2 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username="kittylover123")
        group=Group.objects.get(name='Game_master')
        user_obj.groups.add(group)
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/game_masters')
        
        self.assertEqual(response.status_code, 200)
    
    
    def test_post_GM_page(self):
        """
        Test that a GM user can add advice to the database

        Authors:
            Jessie 
        """
        client = Client()
        g1 = Group.objects.create(name='Game_master')
        g2 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username="kittylover123")
        group=Group.objects.get(name='Game_master')
        user_obj.groups.add(group)
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.post(path='/climate/game_masters', data=
        {
            "link_or_content": "link",
            "content": "test",
            "source":"test"
        })
        advice=Advice.objects.get(source="test")
        self.assertEqual(advice.link,"test")
        self.assertEqual(response.status_code, 200)
    
    def test_player_cannot_access_page(self):
        """
        Test that a player user can't access the GM page

        Authors:
            Jessie 
        """
        client = Client()
        g1 = Group.objects.create(name='Game_masters')
        g2 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj = User.objects.get(username="kittylover123")
        
        response=client.get(path='/climate/game_masters')
        
        self.assertEqual(response.status_code, 302)

    

    

    

    

    

    

class friendTests(TestCase):
    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
    
    def test_friends_redirect(self):
        """
        Tests that the friends page redirects to the login page for an unauthorised user

        Author:
            Jessie, Laurie
        """
        client = Client()
        response=client.get(path='/climate/friend')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login_user?next=/climate/friend")

    def test_friends_page(self):
        """
        Checks that the friends page returns data of a random user in the database (not of the currently logged in user)

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/friend')
        self.assertEqual(response.context["fur_colour"],"#000000,#000000")
        self.assertEqual(response.context['eye_colour'],'#95fdff')
        self.assertEqual(response.context["bottle_num"],0)
        self.assertEqual(response.context["article_num"],0)
        self.assertEqual(response.context["recycle_num"],0)
        self.assertEqual(response.context["friend_username"],"test")
        self.assertEqual(response.context["friend_bottle_num"],0)
        self.assertEqual(response.context["friend_article_num"],0)
        self.assertEqual(response.context["friend_recycle_num"],0)
        self.assertEqual(response.context["f_fur_colour"],"#000000,#000000")
        self.assertEqual(response.context['f_eye_colour'],'#95fdff')
        self.assertEqual(response.status_code, 200)
        
    def test_friends_page_with_url(self):
        """
        Checks that the friends page returns the data of a user specified in the URL

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test2",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/friend/test')
        self.assertEqual(response.context["fur_colour"],"#000000,#000000")
        self.assertEqual(response.context['eye_colour'],'#95fdff')
        self.assertEqual(response.context["bottle_num"],0)
        self.assertEqual(response.context["article_num"],0)
        self.assertEqual(response.context["recycle_num"],0)
        self.assertEqual(response.context["friend_username"],"test")
        self.assertEqual(response.context["friend_bottle_num"],0)
        self.assertEqual(response.context["friend_article_num"],0)
        self.assertEqual(response.context["friend_recycle_num"],0)
        self.assertEqual(response.context["f_fur_colour"],"#000000,#000000")
        self.assertEqual(response.context['f_eye_colour'],'#95fdff')
        self.assertEqual(response.status_code, 200)

    def test_friends_page_with_privacy(self):
        """
        Checks that the friends page doesnt return data on private profiles

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj=User.objects.get(username="test")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.private=True
        user_prof.save()

        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        
        response=client.get(path='/climate/friend')
        self.assertEqual(response.context["fur_colour"],"#000000,#000000")
        self.assertEqual(response.context['eye_colour'],'#95fdff')
        self.assertEqual(response.context["bottle_num"],0)
        self.assertEqual(response.context["article_num"],0)
        self.assertEqual(response.context["recycle_num"],0)
        self.assertEqual(response.context["friend_username"],None)
        self.assertEqual(response.context["friend_bottle_num"],0)
        self.assertEqual(response.context["friend_article_num"],0)
        self.assertEqual(response.context["friend_recycle_num"],0)
        self.assertEqual(response.context["f_fur_colour"],"#ff0000")
        self.assertEqual(response.context['f_eye_colour'],"#ff0000")
        self.assertEqual(response.status_code, 200)
    
    def test_friends_page_with_private_url(self):
        """
        Checks that the friends page doesnt give user data if that user is private

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        client.post(path='/users/register_user', data=
        {
            "username": "test2",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })
        user_obj=User.objects.get(username="test")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.private=True
        user_prof.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/friend/test')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/climate/friend")

class leaderBoardTests(TestCase):
    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )
    
    def test_leaderboard(self):
        """
        Tests the leaderboard page

        Author:
            Jessie, Laurie
        """
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
        #set up users with scores to display
        testuser1 = User.objects.create_user('testUser1', 'test@test.com', 'testPass')
        testkitty1 = Creature.objects.create()
        Profile.objects.create(user=testuser1, creature=testkitty1, points=100)
        testuser2 = User.objects.create_user('testUser2', 'test@test.com', 'testPass')
        testkitty2 = Creature.objects.create()
        Profile.objects.create(user=testuser2, creature=testkitty2, points=90)
        testuser3 = User.objects.create_user('testUser3', 'test@test.com', 'testPass')
        testkitty3 = Creature.objects.create()
        Profile.objects.create(user=testuser3, creature=testkitty3, points=30)
        testuser4 = User.objects.create_user('testUser4', 'test@test.com', 'testPass')
        testkitty4 = Creature.objects.create()
        Profile.objects.create(user=testuser4, creature=testkitty4, points=20)
        testuser5 = User.objects.create_user('testUser5', 'test@test.com', 'testPass')
        testkitty5 = Creature.objects.create()
        Profile.objects.create(user=testuser5, creature=testkitty5, points=80)
        response=client.get(path='/climate/leaderboard')
        leaderboard_data=response.context['data']
        self.assertEqual(leaderboard_data[0]["username"],'testUser1')
        self.assertEqual(leaderboard_data[0]["points"], 100)
        self.assertEqual(leaderboard_data[1]["username"],'testUser2')
        self.assertEqual(leaderboard_data[1]["points"],90)
        self.assertEqual(leaderboard_data[2]["username"],'testUser5')
        self.assertEqual(leaderboard_data[2]["points"],80)
        self.assertEqual(leaderboard_data[3]["username"],'testUser3')
        self.assertEqual(leaderboard_data[3]["points"],30)
        self.assertEqual(leaderboard_data[4]["username"],'testUser4')
        self.assertEqual(leaderboard_data[4]["points"],20)
        self.assertEqual(len(leaderboard_data), 6)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rank'], 6)
       
    def test_rank_in_first(self):
        """
        Tests the leaderboard page

        Author:
            Laurie
        """
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
        #set up users with scores to display
        testuser1 = User.objects.create_user('testUser1', 'test@test.com', 'testPass')
        testkitty1 = Creature.objects.create()
        Profile.objects.create(user=testuser1, creature=testkitty1, points=100)
        testuser2 = User.objects.create_user('testUser2', 'test@test.com', 'testPass')
        testkitty2 = Creature.objects.create()
        Profile.objects.create(user=testuser2, creature=testkitty2, points=90)
        testuser3 = User.objects.create_user('testUser3', 'test@test.com', 'testPass')
        testkitty3 = Creature.objects.create()
        Profile.objects.create(user=testuser3, creature=testkitty3, points=30)
        testuser4 = User.objects.create_user('testUser4', 'test@test.com', 'testPass')
        testkitty4 = Creature.objects.create()
        Profile.objects.create(user=testuser4, creature=testkitty4, points=20)
        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.points = 110
        user_prof.save()
        response=client.get(path='/climate/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rank'], 1)

    def test_leaderboard_redirect(self):
        """
        Tests that the leaderboard page redirects to the login page for an unauthorised user

        Author:
            Jessie, Laurie
        """
        client = Client()
        response=client.get(path='/climate/leaderboard')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/login_user?next=/climate/leaderboard")

class ItemShopTests(TestCase):
    """
    Test block for the item shop view function.
    """

    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )
        Item.objects.create(
            item_id=1,
            item_name="leaf_hat",
            item_cost=50,
            item_class="hat",
            scale=120
            )
        Item.objects.create(
            item_id=2,
            item_name="wizard_hat",
            item_cost=120,
            item_class="hat",
            scale=240
            )
        Item.objects.create(
            item_id=3,
            item_name="top_hat",
            item_cost=80,
            item_class="hat",
            scale=220
            )

    def test_buy_item(self):
        """
        Test that a wearing object is updated in the DB when a item is bought

        Authors:
            Jessie 
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.points = 200
        user_prof.save()

        former_player_balance = user_prof.points

        
        
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/item_shop', data={
            'purchase_new_item':'true',
            'item_id':1
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        wearing = Wearing.objects.get(creature=kitty)
        wearing_item_obj = wearing.item
        self.assertEqual(wearing_item_obj.item_id,1)
        
        

        new_player_balance = user_prof.points

        self.assertEqual(former_player_balance-50, new_player_balance )
        
    def test_buy_item_fail(self):
        """
        Test that a wearing object is not updated in the DB when a item is attempted to be bought but the user
        doesn't have enough points

        Authors:
            Jessie 
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.points = 200
        user_prof.save()

        former_player_balance = user_prof.points

        
        
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/item_shop', data={
            'purchase_new_item':'true',
            'item_id':1
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        wearing = Wearing.objects.get(creature=kitty)
        wearing_item_obj = wearing.item
        self.assertEqual(wearing_item_obj.item_id,1)
        
        

        new_player_balance = user_prof.points

        self.assertEqual(former_player_balance-50, new_player_balance )
    
    def test_view_shop_page(self):
        """
        Test that a wearing object is not updated in the DB when a item is attempted to be bought but the user
        doesn't have enough points

        Authors:
            Jessie 
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.points = 200
        user_prof.save()

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/item_shop')
        self.assertEqual(response.context['username'],"kittylover123")
        self.assertEqual(response.context['points_available'],200)
        self.assertEqual(response.context['fur_colour'],'#000000,#000000')
        self.assertEqual(response.context['eye_colour'],'#95fdff')
        self.assertEqual(response.context['cat_item'],'0')
        self.assertEqual(response.context['cat_item_scale'],'0')
        self.assertTrue((response.context['item_id_1']==1) or (response.context['item_id_1']==2) or (response.context['item_id_1']==3))
        self.assertTrue((response.context['item_price_1']==50) or (response.context['item_price_1']==80) or (response.context['item_price_1']==120))
        self.assertTrue((response.context['item_scale_1']==120) or (response.context['item_scale_1']==220) or (response.context['item_scale_1']==240))
        self.assertTrue((response.context['item_id_2']==1) or (response.context['item_id_1']==2) or (response.context['item_id_1']==3))
        self.assertTrue((response.context['item_price_2']==50) or (response.context['item_price_1']==80) or (response.context['item_price_1']==120))
        self.assertTrue((response.context['item_scale_2']==120) or (response.context['item_scale_1']==220) or (response.context['item_scale_1']==240))
        self.assertTrue((response.context['item_id_3']==1) or (response.context['item_id_1']==2) or (response.context['item_id_1']==3))
        self.assertTrue((response.context['item_price_3']==50) or (response.context['item_price_1']==80) or (response.context['item_price_1']==120))
        self.assertTrue((response.context['item_scale_3']==120) or (response.context['item_scale_1']==220) or (response.context['item_scale_1']==240))
        self.assertEqual(response.context['attempted_purchase'],'false')
        self.assertEqual(response.context['successful_purchase'],'false')
        

    

class ColourShopTests(TestCase):
    """
    Test block for the colour shop view function.
    """

    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.
    
        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#2196f3",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )

    def test_eye_colour_purchase_successful(self):
        """
        Test that a kitty object is updated in the DB when a new eye colour is successfully purchased

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.num_times_watered = 0
        user_prof.num_times_fed = 0
        user_prof.num_times_litter_cleared = 0
        user_prof.points = 10
        user_obj.save()
        user_prof.save()

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        former_eye_colour = kitty.eye_colour
        former_eye_colour_name = former_eye_colour.colour_id
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'true',
            'purchase_new_colour_fur': 'false',
            'eye_colour': '#000000',
            'fur_colour': ''
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        new_eye_colour = kitty.eye_colour
        new_eye_colour_name = new_eye_colour.colour_id
        eye_colour_price = new_eye_colour.colour_cost

        new_player_balance = user_prof.points

        self.assertNotEqual(former_eye_colour_name, new_eye_colour_name)
        self.assertEqual(former_player_balance - eye_colour_price, new_player_balance )

    def test_fur_colour_purchase_successful(self):
        """
        Test that a kitty object is updated in the DB when a new fur colour is successfully purchased

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.num_times_watered = 0
        user_prof.num_times_fed = 0
        user_prof.num_times_litter_cleared = 0
        user_prof.points = 10
        user_obj.save()
        user_prof.save()

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        fur_colour_obj = kitty.fur_colour
        former_fur_colour = fur_colour_obj.colour_hex_val
        former_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'false',
            'purchase_new_colour_fur': 'true',
            'eye_colour': '',
            'fur_colour': '#2196f3,#2196f3'
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        
        fur_colour_obj = kitty.fur_colour
        new_fur_colour = fur_colour_obj.colour_hex_val
        new_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        
        

        new_player_balance = user_prof.points

        self.assertNotEqual(new_fur_colour, former_fur_colour)
        self.assertEqual(former_player_balance - 10, new_player_balance )

    def test_eye_colour_purchase_fail(self):
        """
        Test that a kitty object is not updated in the DB when a new eye colour purchase fails

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        former_eye_colour = kitty.eye_colour
        former_eye_colour_name = former_eye_colour.colour_id
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'true',
            'purchase_new_colour_fur': 'false',
            'eye_colour': '#000000',
            'fur_colour': ''
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        new_eye_colour = kitty.eye_colour
        new_eye_colour_name = new_eye_colour.colour_id
        eye_colour_price = new_eye_colour.colour_cost

        new_player_balance = user_prof.points

        self.assertEqual(former_eye_colour_name, new_eye_colour_name)
        self.assertEqual(former_player_balance , new_player_balance )

    def test_fur_colour_purchase_fail(self):
        """
        Test that a kitty object is not updated in the DB when a new fur colour purchase fails

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        fur_colour_obj = kitty.fur_colour
        former_fur_colour = fur_colour_obj.colour_hex_val
        former_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'false',
            'purchase_new_colour_fur': 'true',
            'eye_colour': '',
            'fur_colour': '#2196f3,#2196f3'
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        
        fur_colour_obj = kitty.fur_colour
        new_fur_colour = fur_colour_obj.colour_hex_val
        new_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        
        

        new_player_balance = user_prof.points

        self.assertEqual(new_fur_colour, former_fur_colour)
        self.assertEqual(former_player_balance, new_player_balance )

    def test_both_colour_purchase(self):
        """
        Test that a kitty object is  updated in the DB when a new fur and eye colour is purchased

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        
        
        user_prof.points = 20
        user_obj.save()
        user_prof.save()

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        fur_colour_obj = kitty.fur_colour
        former_fur_colour = fur_colour_obj.colour_hex_val
        former_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        former_eye_colour = kitty.eye_colour
        former_eye_colour_name = former_eye_colour.colour_id
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'true',
            'purchase_new_colour_fur': 'true',
            'eye_colour': '#000000',
            'fur_colour': '#2196f3,#2196f3'
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        new_player_balance = user_prof.points
        fur_colour_obj = kitty.fur_colour
        new_fur_colour = fur_colour_obj.colour_hex_val
        new_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        new_eye_colour = kitty.eye_colour
        new_eye_colour_name = new_eye_colour.colour_id
        self.assertNotEqual(new_fur_colour, former_fur_colour)
        self.assertNotEqual(new_eye_colour_name, former_eye_colour_name)
        self.assertEqual(former_player_balance-20, new_player_balance )

    def test_both_colour_purchase_fail(self):
        """
        Test that a kitty object is updated correctly (with fur colour only) in the DB when a new fur and eye
        colour is purchased but the user doesn't have enough points for both

        Authors:
            Jessie and Nevan
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        
        
        user_prof.points = 10
        user_obj.save()
        user_prof.save()

        former_player_balance = user_prof.points

        kitty = user_prof.creature
        fur_colour_obj = kitty.fur_colour
        former_fur_colour = fur_colour_obj.colour_hex_val
        former_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        former_eye_colour = kitty.eye_colour
        former_eye_colour_name = former_eye_colour.colour_id
        

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'true',
            'purchase_new_colour_fur': 'true',
            'eye_colour': '#000000',
            'fur_colour': '#2196f3,#2196f3'
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        kitty = user_prof.creature
        new_player_balance = user_prof.points
        fur_colour_obj = kitty.fur_colour
        new_fur_colour = fur_colour_obj.colour_hex_val
        new_fur_colour_patches= fur_colour_obj.colour_hex_val_patch
        new_eye_colour = kitty.eye_colour
        new_eye_colour_name = new_eye_colour.colour_id
        self.assertNotEqual(new_fur_colour, former_fur_colour)
        self.assertEqual(new_eye_colour_name, former_eye_colour_name)
        self.assertEqual(former_player_balance-10, new_player_balance )

    def test_view_colour_shop_page(self):
        """
        Test that a wearing object is not updated in the DB when a item is attempted to be bought but the user
        doesn't have enough points

        Authors:
            Jessie 
        """
        client = Client()
        players_group = Group.objects.create(name='Player')
        client.post(path='/users/register_user', data=
        {
            "username": "kittylover123",
            "email": "kittylover@climatecare.com",
            "password1": "i_secretly_hate_kitties",
            "password2": "i_secretly_hate_kitties"
        })

        user_obj = User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.points = 200
        user_prof.save()

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.get(path='/climate/colour_shop')
        self.assertEqual(response.context['username'],"kittylover123")
        self.assertEqual(response.context['points_available'],200)
        self.assertEqual(response.context['fur_colour'],'#000000,')
        self.assertEqual(response.context['eye_colour'],'#2196f3')
        self.assertEqual(response.context['attempted_purchase'],'false')
        self.assertEqual(response.context['successful_purchase'],'false')    

        

       


   

    

class SettingsTests(TestCase):
    def setUp(self):
        """
        Sets up the colour objects needed for foreign referencing when
        creating new cats. These are the colours needed for the default
        fields.

        Author:
            Nevan
        """
        Colour.objects.create(
            colour_id="black",
            colour_hex_val="#000000",
            colour_hex_val_patch="#000000",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blue",
            colour_hex_val="#95fdff",
            colour_hex_val_patch="#95fdff",
            colour_cost=10
        )
        Colour.objects.create(
            colour_id="blueP",
            colour_hex_val="#2196f3",
            colour_hex_val_patch="#2196f3",
            colour_cost=10
        )

    def test_start_pause_functionality(self):
        '''
        Checks that a user successfully adjusts their data
        when they attempt to pause their game.

        Authors: Laurie
        '''
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
        user_obj=User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.paused, False)
        client.post(path='/climate/settings', data={
             "pause_data":"True",
             "current_username": "",
             "current_password":"",
             "privacy_setting":"False"
        })
        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.paused, True)
        response = client.get(path='/climate/settings')
        self.assertEqual(response.context["is_paused"],True)
    
    def test_end_pause_functionality(self):
        '''
        Checks that a user successfully adjusts their data
        when they attempt to end the pause on their game.

        Authors: Laurie
        '''
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
        user_obj=User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.paused = True
        user_prof.save()
        client.post(path='/climate/settings', data={
             "pause_data":"False",
             "current_username": "",
             "current_password":"",
             "privacy_setting":"False"
        })
        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.paused, False)
        response = client.get(path='/climate/settings')
        self.assertEqual(response.context["is_paused"],False)

    def test_make_public(self):
        '''
        Checks that a user successfully adjusts their data
        when they attempt to make their profile private.

        Authors: Jessie
        '''
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
        user_obj=User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        user_prof.private=True
        user_prof.save()
        client.post(path='/climate/settings', data={
             "pause_data":"False",
             "current_username": "",
             "current_password":"",
             "privacy_setting":"False"
        })
        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.private, False)
        response = client.get(path='/climate/settings')
        self.assertEqual(response.context["is_private"],False)

    def complex_pause_test(self):
        '''
        A more complex test for the settings page that checks the pause functionality
        and whether it accurately returns the refill dates to the right times.

        Authors: Laurie
        '''
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
        user_obj=User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        cat_data = user_prof.creature
        currentTime = timezone.now()
        user_prof.pause_time = currentTime-timedelta(days=3)
        user_prof.paused = True
        pastTime=currentTime-timedelta(days=5)
        cat_data.last_food_refill = pastTime
        cat_data.save()
        user_prof.save()
        client.post(path='/climate/settings', data={
             "pause_data":"False",
             "current_username": "",
             "current_password":"",
             "privacy_setting":"False"
        })
        user_prof = Profile.objects.get(user=user_obj)
        cat_data = user_prof.creature
        self.assertEqual(cat_data.last_food_refill, timezone.now()-timedelta(days=2))

    def change_password_valid(self):
        '''
        Successfully changes a users password, and then allows
        them to log into the system with the updated password.

        Authors: Laurie
        '''
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
        client.post(path='/climate/settings', data={
             "pause_data":"",
             "current_username": "",
             "current_password":"i_secretly_hate_kitties",
             "new_password":"i_actually_love_kitties",
             "new_password2":"i_actually_love_kitties",
             "privacy_setting":"False"
        })
        client.logout()
        response = client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_actually_love_kitties"
        })
        response2=client.get(path='/climate/kitty')
        self.assertTrue(response2.context['user'].is_authenticated)
        self.assertEqual(response2.status_code, 200)

    def change_password_invalid_wrong_current(self):
        '''
        Unsuccessfully tries to change a user's password, due to current
        password being incorrect. Fails a login with new password.

        Authors: Laurie
        '''
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
        client.post(path='/climate/settings', data={
             "pause_data":"",
             "current_username": "",
             "current_password":"i_openly_hate_kitties",
             "new_password":"i_actually_love_kitties",
             "new_password2":"i_actually_love_kitties",
             "privacy_setting":"False"
        })
        client.logout()
        response2 = client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_openly_love_kitties"
        })
        response2=client.get(path='/climate/kitty')
        self.assertFalse(response2.context['user'].is_authenticated)
        self.assertEqual(response2.status_code, 302)

    def change_password_invalid_wrong_new(self):
        '''
        Unsuccessfully tries to change a user's password, due to different
        passwords being entered for a new password. Fails a login with new password.

        Authors: Laurie
        '''
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
        client.post(path='/climate/settings', data={
             "pause_data":"",
             "current_username": "",
             "current_password":"i_secretly_hate_kitties",
             "new_password":"i_actually_love_kitties",
             "new_password2":"i_actually_adore_kitties",
             "privacy_setting":"False"
        })
        client.logout()
        response2 = client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_actually_love_kitties"
        })
        response2=client.get(path='/climate/kitty')
        self.assertFalse(response2.context['user'].is_authenticated)
        self.assertEqual(response2.status_code, 302)

    def change_username(self):
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
        client.post(path='/climate/settings', data={
             "pause_data":"",
             "current_username": "kittyhater123",
             "current_password":"",
             "new_password":"",
             "new_password2":"",
             "privacy_setting":"False"
        })
        client.logout()
        response2 = client.post(path='/users/login_user', data=
        {
            "username": "kittyhater123",
            "password": "i_actually_love_kitties"
        })
        self.assertTrue(response2.context['user'].is_authenticated)
        self.assertEqual(response2.status_code, 200)

    def test_make_private(self):
        '''
        Checks that a user successfully adjusts their data
        when they attempt to make their profile private.

        Authors: Jessie
        '''
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
        user_obj=User.objects.get(username="kittylover123")
        user_prof = Profile.objects.get(user=user_obj)
        client.post(path='/climate/settings', data={
             "pause_data":"False",
             "current_username": "",
             "current_password":"",
             "privacy_setting":"True"
        })
        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.private, True)
        response = client.get(path='/climate/settings')
        self.assertEqual(response.context["is_private"],True)

    def test_check_private_default(self):
        '''
        Checks that a user profile is automatically set to public

        Authors: Jessie
        '''
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
        user_obj=User.objects.get(username="kittylover123")

        user_prof = Profile.objects.get(user=user_obj)
        self.assertEqual(user_prof.private, False)
        response = client.get(path='/climate/settings')
        self.assertEqual(response.context["is_private"],False)
    


class GeoLocationTests(TestCase):
    """
    Test block to test geolocation functionality.

    Author:
        Lucia
    """
    
    def test_within_dist(self):
        """
        Tests whether a user can be considered to be in or out of range of certain coordinates.

        Author:
            Lucia
        """
        loc1 = (28.426846, 77.088834)
        loc2 = (28.394231, 77.050308)

        self.assertFalse(within_distance(loc1, loc2, 10))
        self.assertTrue(within_distance(loc1, loc2, 6000))
