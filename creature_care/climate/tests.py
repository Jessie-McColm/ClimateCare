from django.test import TestCase
from django.urls import reverse
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
        self.assertIs(False, False)


class KittyIndexTests(TestCase):
    #class to check that the data returned from the kitty view is correct

    def test_unauthorised_user(self):
        #i guess test if various DB functions work?
        self.assertIs(False, False)
