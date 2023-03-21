"""
The code used to generate all of the databases to be used within ClimateCare
"""

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# NOTE: Classes that reference other classes must be below the class that they reference



class Colour(models.Model):
    """
This class describes the model for containing hex values of possible colours of the 
cat's colours and eyes.

Author:
    Nevan
"""
    colour_id = models.CharField(primary_key=True, max_length=16)
    colour_hex_val = models.CharField(max_length=10)
    colour_hex_val_patch = models.CharField(max_length=10, default="", null=True)
    colour_cost = models.IntegerField(null=False, default=0)



# the thirst, litter and food integers shall remain strictly in the domain of 1-100
class Creature(models.Model):
    """
This class contains all the information regarding a "Creature" which is assigned to each user in a one-to-one
relationship. The Creature's primary ID is its CreatureID and the attributes that will vary the most are its
thirst, litter and food values.

Authors:
    Laurie and Nevan

"""
    creature_id = models.AutoField(primary_key=True)
    name = models.CharField(default="Creature", max_length=50)

    eye_colour = models.ForeignKey(Colour, on_delete=models.SET_DEFAULT, default="blue", related_name="eye_colour")
    fur_colour = models.ForeignKey(Colour, on_delete=models.SET_DEFAULT, default="black", related_name="fur_colour")

    thirst = models.IntegerField(
        default=0  # django does not support min/max values for ints, so min/max values must be enforced elsewhere
    )

    last_thirst_refill = models.DateTimeField(default=now)
    litter = models.IntegerField(default=0)
    last_litter_refill = models.DateTimeField(default=now)
    food = models.IntegerField(default=0)
    last_food_refill = models.DateTimeField(default=now)


# NOTE access_level will most likely either be 1 or 2 in implementation and no other value
class Profile(models.Model):
    """
This class contains part of the information associated with each user of the system in place. Each Profile
entity connects to an entry in the Users database, which stores additional information about a user
such as the username, password and email address. The Profile class contains extra information crucial to our
system, such as creature_id and points.

Authors:
    Laurie and Nevan
"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_id = models.AutoField(primary_key=True)
    points = models.IntegerField(default=0)
    access_level = models.IntegerField(null=False, default=1)  # eh, maybe get rid of?
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    num_times_watered = models.IntegerField(default=0, null=False)
    num_times_fed = models.IntegerField(default=0, null=False)
    num_times_litter_cleared = models.IntegerField(default=0, null=False)
    paused = models.BooleanField(default=False, null=False)
    private = models.BooleanField(default=False, null=False)
    pause_time = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-points']



class Item(models.Model):
    """
This class contains information regarding each object existing within a system that a user
can "purchase" with earned points in order to customise their cat for their own 
satisfaction. 

Authors:
    Laurie and Nevan
"""
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=40)
    item_cost = models.IntegerField(null=False, default=0)
    item_class = models.CharField(max_length=25, null=False)
    scale = models.IntegerField(default=120, null=False)



class Wearing(models.Model):
    """
This class simply establishes a many to many relationship between Creature and Item

Authors:
    Laurie and Nevan
"""
    wearing_id = models.AutoField(primary_key=True)
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, default=None)



class Advice(models.Model):
    """
This class stores information regarding the advice a Creature may share when being "fed". This 
knowledge base is adjusted by game masters or developers and randomly broadcast by the Creature.

Authors:
    Laurie and Nevan
"""
    advice_id = models.AutoField(primary_key=True)
    link = models.CharField(max_length=500, default="")
    content = models.CharField(max_length=500, default="")
    source = models.CharField(max_length=250, default="")



class LocationBin(models.Model):
    """
This class stores location information of a specific "bin" or otherwise entity

Authors:
    Nevan
"""
    location_id = models.IntegerField(primary_key=True, unique=True)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)


class LocationFountain(models.Model):
    """
This class stores location information of a specific "water fountain" or otherwise entity

Authors:
    Nevan
"""
    location_id = models.IntegerField(primary_key=True, unique=True)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
