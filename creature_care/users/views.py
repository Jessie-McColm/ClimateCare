from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from climate.models import Profile,Creature


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


def create_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        #try to see if there are any users in the DB with the same username
        #if no duplicates:
        #check if passwrod is good enough/long enough
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    
       # b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
        #b.save()
        #check if successful
        #if success:
            #return redirect('login_user')
        #else if failure
            #return render(request, 'whatever name is', {some data about error}) (do this for password and username failures too)
    else:
        return render(request,'I dont know what to call this')

            
