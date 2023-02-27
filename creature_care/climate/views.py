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
from .models import Profile,Creature,Advice,LocationBin,LocationFountain
import random

from django.contrib.auth.decorators import login_required

# requires import!!!!
import haversine as hs
from haversine import Unit

'''
The main page of the project, accessed using /kitty/. Displays the creature and shows its current state,
while providing functionality to feed/water/clean it. Uses geolocation functionality to verify whether a
user is within a sensible distance from a fountain/bin

request = the POST sent from the website containing the user query 
'''
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
    coordinates = request.POST.get('coordinates')
    if request.method == "POST":
            #set null coordinates for feeding
            task = request.POST.get('task')
            if task=="water":
                total_fountains = len(list(LocationFountain.objects.all())) #gets the number of fountains possible
                location_counter = 0 #counter used to iterate through LocationFountain.objects.all()
                success = False #boolean to confirm a location has been found
                while ((success == False) and (location_counter != total_fountains - 1)): #iterates through
                    #every single location, checking if the user is within distance
                    current_fountain = list(LocationFountain.objects.all())[location_counter]
                    success = within_distance((coordinates[0], coordinates[1]), (current_fountain.latitude, current_fountain.longitude), 100)
                    location_counter = location_counter + 1
                if (success == True): #if a valid location is found, this condition is chosen
                    print(coordinates, task)
                    cat_data.last_thirst_refill=currentTime  #(is this how you edit?)
                    cat_data.save()
                    #can we play a little animation?
                    info['task']='water'
                else: #if no valid location is found, this condition is chosen
                    #error display maybe?
                    print("not within distance")
            if task=="litter":
                total_bins = len(list(LocationBin.objects.all())) #gets the number of bins possible
                location_counter = 0
                success = False 
                while ((success == False) and (location_counter != total_bins - 1)):
                    current_bin = list(LocationBin.objects.all())[location_counter]
                    success = within_distance((coordinates[0], coordinates[1]), (current_bin.latitude, current_bin.longitude), 200)
                    location_counter = location_counter + 1
                if (success == True): #if a valid location is found, this condition is chosen
                    print(coordinates, task)
                    cat_data.last_litter_refill=currentTime  
                    cat_data.save() 
                    #can we play a little animation?
                    info['task']='clean'
                else: #if no valid location is found, this condition is chosen
                    #error display maybe?
                    print("not within distance")
            
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
    location1 = LocationFountain(longitude=0, latitude=0)
    location2 = LocationBin(longitude=0, latitude=0)
    location1.save()
    location2.save()
    #-----------------
    #Gets the info you need (in this block for now for clarity)
    #username = request.user.get_username()
   
    # can also use this: User.objects.get(username = username) 
    #user_obj =  request.user

    #user_prof=Profile.objects.get(user = user_obj)
    #cat_data= user_prof.creature
    
    #-----------------
    
    #colour = cat_data.colour
    #name = cat_data.name

    # Laurie and jessie added the above commands for testing the databases

    #Laurie: these lines were used to generate some simple example articles 
    # new_advice1 = Advice(link="https://example.com", source="example")
    # new_advice2 = Advice(content="example advice", source ="example2")
    # new_advice3 = Advice(content="second example advice", source ="example3")
    # new_advice4 = Advice(content="third example advice", source ="example4")
    # new_advice1.save()
    # new_advice2.save()
    # new_advice3.save()
    # new_advice4.save()

    # if request.user.is_authenticated:
    # Do something for authenticated users.
    # userID=request.session['userID']
    # can then make a DB request to get needed info? - actually may need extra
    # security - can someone just set an arbitrary session variable?
    
    # else:
    # Do something for anonymous users.
    
    return HttpResponse()

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
Calculates haversine distance (not euclidean) and returns if within distance

Args:
    user_loc: tuple of user location (lattitude, longitude)
    object_loc: tuple of object location (lattitude, longitude)
    m_dist: maximum desired distance between objects

Returns:
    Boolean whether in range of not

"""
def within_distance(user_loc, object_loc, m_dist):

    # using haversine distance not eulcidean
    
    #To calculate distance in meters 
    o_dist = hs.haversine(user_loc,object_loc, unit=Unit.METERS)

    if o_dist <= m_dist:
        in_range = True
    else:
        in_range = False
    
    return in_range

