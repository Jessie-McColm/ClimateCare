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
#Create your views here.


def kitty(request):
    #return HttpResponse("Hello, world. You're at the kitty.")
    #will pass a dict of various DB info gotten from the user - can this be handled in html?
    if request.user.is_authenticated:
        #calculating the time difference to determine how stinky/thirsty/ etc the kitty is
        #better to calculate each time we send page cause changes depending on current time
        threeDays=259200
        currentTime = datetime.datetime.now()
        info={}
        userID=request.session['userID']
        userProf=Profile.objects.get(user=userID)
        catData=Creature.objects.get(creature_id=userProf.creature_id)
        info['colour']=catData.colour
        info['name']=catData.name
        waterTimeDifference= currentTime-catData.last_thirst_refill
        litterTimeDifference= currentTime-catData.last_litter_refill
        foodTimeDifference= currentTime-catData.last_food_refill
        waterTimeDifferenceSeconds = waterTimeDifference.total_seconds()
        litterTimeDifferenceSeconds= litterTimeDifference.total_seconds()
        foodTimeDifferenceSeconds=foodTimeDifference.total_seconds()
        if waterTimeDifferenceSeconds > threeDays:
            info['thirsty']=True
        else:
            info['thirsty']=False

        if litterTimeDifferenceSeconds > threeDays:
            info['stinky']=True
        else:
            info['stinky']=False

        if foodTimeDifferenceSeconds > threeDays:
            info['hungry']=True
        else:
            info['hungry']=False
            
        
        
        
        
        
    return render(request, 'cat.html',info)

def articles(request):
    

    #if request.user.is_authenticated:
    # Do something for authenticated users.
    #userID=request.session['userID']
    #can then make a DB request to get needed info? - actually may need extra
    #security - can someone just set an arbitrary session variable?
    
    #else:
    # Do something for anonymous users.
    
    return HttpResponse("article page")




