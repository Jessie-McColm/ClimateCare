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
from .models import Profile,Creature,Advice
import random

from django.contrib.auth.decorators import login_required

#Create your views here.

# this decorator means if not logged in sends back to login page
# might want to change in future 
@login_required(login_url='loginPage')
def kitty(request):
    
   # return render(request, 'cat.html')
    #will pass a dict of various DB info gotten from the user - can this be handled in html?

    #-----------------
    #Gets the info you need (in this block for now for clarity)
    username = request.user.get_username()
   
    # can also use this: User.objects.get(username = username) 
    user_obj =  request.user

    user_prof=Profile.objects.get(user = user_obj)
    cat_data= user_prof.creature
    
    #-----------------
    
    #calculating the time difference to determine how stinky/thirsty/ etc the kitty is
    #better to calculate each time we send page cause changes depending on current time
    threeDays=259200
    currentTime = timezone.now()
    info={}
    info['watered']=False
    info['cleaned']=False

    info['colour'] = cat_data.colour
    info['name'] = cat_data.name
    info['task']="none"

    if request.method == "POST":
            #set null coordinates for feeding
            coordinates = request.POST.get('coordinates')
            task = request.POST.get('task')
            if task=="water":
                '''
                perform some calculations to see if in range of a fountain
                if success'''
                cat_data.last_thirst_refill=currentTime  #(is this how you edit?)
                cat_data.save() 
                #can we play a little animation?
                info['task']='water'
        
            if task=="litter":
            
                '''
                perform some calculations to see if in range of a bin
                if success'''
                cat_data.last_litter_refill=currentTime  
                cat_data.save() 
                #can we play a little animation?
                info['task']='clean'
            
            if task == "feed":
                cat_data.last_food_refill=currentTime  #(is this how you edit?)
                cat_data.save() 
                #can we play a little animation?
                info['task']='feed'
        

    
    water_time_difference= currentTime-cat_data.last_thirst_refill
    litter_time_difference= currentTime-cat_data.last_litter_refill
    food_time_difference= currentTime-cat_data.last_food_refill
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

    #-----------------
    #Gets the info you need (in this block for now for clarity)
    username = request.user.get_username()
   
    # can also use this: User.objects.get(username = username) 
    user_obj =  request.user

    user_prof=Profile.objects.get(user = user_obj)
    cat_data= user_prof.creature
    
    #-----------------
    
    colour = cat_data.colour
    name = cat_data.name

    # Laurie and jessie added these commands for testing the databases
        
    # if request.user.is_authenticated:
    # Do something for authenticated users.
    # userID=request.session['userID']
    # can then make a DB request to get needed info? - actually may need extra
    # security - can someone just set an arbitrary session variable?
    
    # else:
    # Do something for anonymous users.
    
    return HttpResponse(name)

def page_not_found_view(request, exception):
    return render(request, 'notFound.html', status=404)

'''
This function retrieves a random piece of advice available in the Advice database.

Output is a list of data, the first item being "link" or "message". This determines
whether the user will be simply given a link to click or message to read. The second
item is either 1) the link or 2) the content. The third item is always the source of
the information.
'''
def retrieveAdvice():
    random_population = list(Advice.objects.all())
    advice_object = random.choice(random_population) 
    content = advice_object.content
    link = advice_object.link
    source = advice_object.source
    if (content == ""):
        return ["link", link, source]
    else:
        return ["message", content, source]
    
"""
Expects tuple of user location (lattitude, longitude)
Also takes loction of object we want to check its in range of (lattitude, longitude)

"""
def calculate_distance(user_loc, object_loc):
    user_lat = user_loc[0]
    user_long = user_loc[1]

    obj_lat = object_loc[0]
    obj_long = user_loc[1]
