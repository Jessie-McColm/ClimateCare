from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.

def login_user(request):

    # if go to page and actually do something
    if request.method == "POST":
        # name passing in from the html name field
        #username = request.POST['username'] changed to below
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # error here as need to look into the users we have and these argguments etc
        #user = authenticate(request, username, password)
        
        #if user is not None:
            #login(request, user)
            # return succes page
            #return redirect('climate')
        #else:
            #messages.success(request, ("There was an error logging in. Please try again"))
            #return redirect('login')



    return render(request, 'authenticate/login.html', {})