from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import authenticate, login,logout
from .models import Profile,Creature
import datetime

from django.contrib.auth.decorators import login_required

#Create your views here.

# this decorator means if not logged in sends back to login page
# might want to change in future 
@login_required(login_url='loginPage')
def kitty(request):
    
   # return render(request, 'cat.html')
    #will pass a dict of various DB info gotten from the user - can this be handled in html?

    
    #calculating the time difference to determine how stinky/thirsty/ etc the kitty is
    #better to calculate each time we send page cause changes depending on current time
    threeDays=259200
    currentTime = timezone.now()
    info={}
    info['watered']=False
    info['cleaned']=False
    #userID=request.session['username']
    userObj = User.objects.get(username = "poor little meow meow")
    userProf=Profile.objects.get(user = userObj)
    catData=userProf.creature
    info['colour']=catData.colour
    info['name']=catData.name
    info['task']="none"
    if request.method == "POST":
            #set null coordinates for feeding
            coordinates = request.POST.get('coordinates')
            task = request.POST.get('task')
            if task=="water":
                '''
                perform some calculations to see if in range of a fountain
                if success'''
                catData.last_thirst_refill=currentTime  #(is this how you edit?)
                catData.save() 
                #can we play a little animation?
                info['task']='water'
        
            if task=="litter":
            
                '''
                perform some calculations to see if in range of a bin
                if success'''
                catData.last_litter_refill=currentTime  
                catData.save() 
                #can we play a little animation?
                info['task']='clean'
            
            if task == "feed":
                catData.last_food_refill=currentTime  #(is this how you edit?)
                catData.save() 
                #can we play a little animation?
                info['task']='feed'
        
    water_time_difference= currentTime-catData.last_thirst_refill
    litter_time_difference= currentTime-catData.last_litter_refill
    food_time_difference= currentTime-catData.last_food_refill
    water_time_difference_seconds = water_time_difference.total_seconds()
    litter_time_difference_seconds= litter_time_difference.total_seconds()
    food_time_difference_seconds=food_time_difference.total_seconds()
    if water_time_difference_seconds > threeDays:
        info['thirsty']=True
    else:
        info['thirsty']=False

    if litter_time_difference_seconds > threeDays:
        info['stinky']=True
    else:
        info['stinky']=False

    if food_time_difference_seconds > threeDays:
        info['hungry']=True
    else:
        info['hungry']=False
    return render(request, 'cat.html',info)

@login_required(login_url='loginPage')
def articles(request):
    #meowmeow = User.objects.create_user('bg', 'lennon@thebeatles.com', 'meowmeowmeow')
    #kitty = Creature()
    #profile = Profile(user=meowmeow, creature=kitty)
    #kitty.save()
    #profile.save()
    #test_username = meowmeow.username
    userObj = User.objects.get(username = "poor little meow meow")
    userProf=Profile.objects.get(user = userObj)
    catData=userProf.creature
    colour = catData.colour
    name = catData.name

    #Laurie and jessie added these commands for testing the databases
        
    #if request.user.is_authenticated:
    # Do something for authenticated users.
    #userID=request.session['userID']
    #can then make a DB request to get needed info? - actually may need extra
    #security - can someone just set an arbitrary session variable?
    
    #else:
    # Do something for anonymous users.
    
    return HttpResponse(name)

def page_not_found_view(request, exception):
    return render(request, 'notFound.html', status=404)

def retrieveAdvice():
    #pick a random value to select some advice from the model
    #return data
    return 0