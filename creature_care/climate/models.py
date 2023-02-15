from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# NOTE: Classes that reference other classes must be below the class that they reference... for some reason.
class Creature(models.Model):
    creature_id = models.IntegerField(primary_key=True, auto_created=True, unique=True)
    name = models.CharField(default="Creature", max_length=50)
    colour = models.CharField(default="black", max_length=16, null=False)  #colour names should be converted to hex values at some point
    thirst = models.IntegerField(default=0)  #django does not support min/max values for ints, so min/max values must be enforced elsewhere
    last_thirst_refill = models.DateTimeField()
    litter = models.IntegerField(default=0)
    last_thirst_refill = models.DateTimeField()
    food = models.IntegerField(default=0)
    last_food_refill = models.DateTimeField()


'''
doc string :D
'''


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_id = models.IntegerField(primary_key=True, unique=True)
    points = models.IntegerField(default=0)
    access_level = models.IntegerField(null=False, default=1)  #eh, maybe get rid of?
    creature_id = models.ForeignKey(Creature, on_delete=models.CASCADE)
    num_times_watered = models.IntegerField(default=0, null=False)
    num_times_fed = models.IntegerField(default=0, null=False)
    num_times_litter_cleared = models.IntegerField(default=0, null=False)


class Item(models.Model):
    item_id = models.IntegerField(primary_key=True, unique=True)
    item_name = models.CharField(max_length=40)
    item_cost = models.IntegerField(null=False)
    item_img = models.FileField()  #reconsider later, may need to do CSS files instead of jpg/png/whatever
    item_class = models.CharField(max_length=25, null=False)


class Wearing(models.Model):
    wearing_id = models.IntegerField(primary_key=True, unique=True)
    creature_id = models.ForeignKey(Creature, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)


class Advice(models.Model):
    advice_id = models.IntegerField(primary_key=True, unique=True)
    content = models.CharField(max_length=500)
    source = models.CharField(max_length=250)
