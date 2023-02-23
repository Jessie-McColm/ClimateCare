from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from climate.models import Creature, Profile

# Create your tests here.

def create_user(user_data,kitty_data,profile_data):
    #set up a dummy user
    pass
def delete_user(userID):
    #clean up the DB
    pass

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
        #i guess test if various DB functions work?
        self.assertIs(False, False)

    def test_authorised_user(self):
        #test if a given user returns a page with the correct data
        self.assertIs(False, False)

    def test_post_articles(self):
        #test if valid response if given when a post request is sent to get articles/feed the kitty
        self.assertIs(False, False)

    def test_post_water(self):
        #test if valid response if given when a post request is sent to water the kitty
        self.assertIs(False, False)

    def test_post_clean(self):
        #test if valid response if given when a post request is sent to clean the kitty
        self.assertIs(False, False)



