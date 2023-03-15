from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from climate.models import Creature, Profile, LocationFountain, LocationBin, Advice, Colour
from django.test import Client
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
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


    def test_unauthorised_user(self):
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
    '''  
    def test_post_articles_DB_update(self):
        """
        Test if database is updated correctly when a post request is sent to get articles/feed the kitty

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
        cat_data = user_prof.creature
        pastTime=timezone.now()-timedelta(seconds=5)
        setattr(cat_data, "last_food_refill", pastTime)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"feed"})
        
        current_time=timezone.now()
        food_time_difference = current_time - cat_data.last_food_refill
        food_time_difference_seconds = food_time_difference.total_seconds()
        self.assertTrue(food_time_difference_seconds<4.0)
        self.assertEqual(response.status_code, 200)
    '''
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
    '''
    def test_post_water_DB_update(self):
        """
        Test if database is updated correctly when a post request is sent to water the kitty

        Author:
            Jessie
        """
        client = Client()
        g1 = Group.objects.create(name='Player')
        print(timezone.now())
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
        pastTime=timezone.now()-timedelta(seconds=5)
        setattr(cat_data, "last_thirst_refill", pastTime)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })
        print(timezone.now())
        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"water"})
        print(cat_data.last_thirst_refill)
        current_time=timezone.now()
        
        water_time_difference = current_time - cat_data.last_thirst_refill
        water_time_difference_seconds = water_time_difference.total_seconds()
        self.assertTrue(water_time_difference_seconds<4)
        self.assertEqual(response.status_code, 200)
    '''
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

    '''
    def test_post_clean_DB_update(self):
        """
        Test if database is updated correctly when a post request is sent to clean the kitty

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
        cat_data = user_prof.creature
        pastTime=timezone.now()-timedelta(seconds=5)
        setattr(cat_data, "last_litter_refill", pastTime)
        cat_data.save()
        client.post(path='/users/login_user', data=
        {
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        response=client.post(path='/climate/kitty', data=
                             {"coordinates":"0,0",
                              "task":"litter"})
        current_time=timezone.now()
        clean_time_difference = current_time - cat_data.last_litter_refill
        clean_time_difference_seconds = clean_time_difference.total_seconds()
        print(clean_time_difference_seconds)
        self.assertEqual(response.context['task'],"clean")
        self.assertTrue(clean_time_difference_seconds<4)
        self.assertEqual(response.status_code, 200)
    '''
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
        advice1 = Advice.objects.create(link="https://example.com", source="admin")
        advice2 = Advice.objects.create(content="this is some advice!", source="admin")
        self.assertEqual(len(list(Advice.objects.all())), 2)

    def test_advice_url(self):
        """
        Testing if advice data is sent back correctly when a request is made to climate/kitty/articles

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
        Sets up a creature object that has not been watered in over 3 days, so should be judged as "thirsty"

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
        response = client.get(path='/climate/my_stats')
        self.assertEqual(response.context['username'], 'kittylover123')
        self.assertEqual(response.context['bottle_num'], 27)
        self.assertEqual(response.context['article_num'], 40)
        self.assertEqual(response.context['recycle_num'], 13)

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

    def test_eye_colour_purchase_successful(self):
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
        user_obj.save()
        user_prof.save()

        client.post(path='/users/login_user', data={
            "username": "kittylover123",
            "password": "i_secretly_hate_kitties"
        })

        client.post(path='/climate/colour_shop', data={
            'purchase_new_colour_eyes': 'true',
            'purchase_new_colour_fur': 'false',
            'eye_colour': '#95fdff,#95fdff',
            'fur_colour': ''
        })

        kitty.save(update_fields=['eye_colour'])

        new_eye_colour = kitty.eye_colour
        new_eye_colour_name = new_eye_colour.colour_id
        eye_colour_price = new_eye_colour.colour_cost

        new_player_balance = user_prof.points

        self.assertNotEqual(former_eye_colour_name, new_eye_colour_name)
        self.assertEqual(former_player_balance, new_player_balance - eye_colour_price)


    # def test_shop_view(self):
    #     """
    #     Tests that the shop view sends back item info correctly

    #     Author:
    #         Jessie
    #     """
    #     client = Client()
    #     g1 = Group.objects.create(name='Player')
    #     client.post(path='/users/register_user', data=
    #     {
    #         "username": "kittylover123",
    #         "email": "kittylover@climatecare.com",
    #         "password1": "i_secretly_hate_kitties",
    #         "password2": "i_secretly_hate_kitties"
    #     })
    #     client.post(path='/users/login_user', data=
    #     {
    #         "username": "kittylover123",
    #         "password": "i_secretly_hate_kitties"
    #     })
    #     testItem1 = Item(item_name="test1", item_cost=30, item_img="static/cat-face.png", item_class="test" )
    #     testItem2 = Item(item_name="test2", item_cost=40, item_img="static/cat-face.png", item_class="test" )
    #     testItem3 = Item(item_name="test3", item_cost=50, item_img="static/cat-face.png", item_class="test" )
    #     response=client.get(path='/climate/shop')
    #     itemList=response.context['items']
    #     self.assertEqual(itemList[0][0],'test1')
    #     self.assertEqual(itemList[0][1],30)
    #     self.assertEqual(itemList[1][0],'test2')
    #     self.assertEqual(itemList[1][1],40)
    #     self.assertEqual(itemList[2][0],'test3')
    #     self.assertEqual(itemList[2][1],50)
    #     self.assertEqual(response.status_code, 200)

    # def test_shop_redirect(self):
    #     """
    #     Tests that the shop page redirects to the login page for an unauthorised user

    #     Author:
    #         Jessie
    #     """
    #     response=client.get(path='/climate/shop')
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, "/users/login_user?next=/climate/shop")


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
