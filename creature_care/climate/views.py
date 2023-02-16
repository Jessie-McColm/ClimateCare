from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import authenticate, login,logout

# Create your views here.


def kitty(request):
    #return HttpResponse("Hello, world. You're at the kitty.")
    #will pass a dict of various DB info gotten from the user - can this be handled in html?
    return render(request, 'cat.html')

def articles(request):
    

    #if request.user.is_authenticated:
    # Do something for authenticated users.
    #userID=request.session['userID']
    #can then make a DB request to get needed info? - actually may need extra
    #security - can someone just set an arbitrary session variable?
    
    #else:
    # Do something for anonymous users.
    
    return HttpResponse("article page")




