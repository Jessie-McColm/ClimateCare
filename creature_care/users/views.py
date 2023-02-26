from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from climate.models import Profile, Creature

from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm


# Create your views here.


def register_user(request):
    # gets form I have put in forms.py which we can customise later

    # if user already loggged in, redirect to the home kitty page
    if request.user.is_authenticated:
        return redirect('kitty')
    # this is a test thing

    else:
        form = CreateUserForm()

        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                # makes user :))
                form.save()

                # can get these messages to show up on page later
                # also way of accessing data 
                user = form.cleaned_data.get('username')
                messages.success(request, "Account was created for " + user)

                # -------------------
                # creates a creature and a profile for the user 
                user_obj = User.objects.get(username = user)
                user_creature = Creature()
                profile = Profile(user=user_obj, creature=user_creature)
                user_creature.save()
                profile.save()
                # ------------------

                return redirect('loginPage')

        context = {'form':form}
        return render(request, 'authenticate/register.html', context)


def login_user(request):
    # if user already logged in, redirect to the home kitty page
    if request.user.is_authenticated:
        return redirect('kitty')

    else:

        # if you go to page and actually do something
        if request.method == "POST":
            # name passing in from the html name field
            # username = request.POST['username'] changed to below
            username = request.POST.get('username')
            password = request.POST.get('password')
            # error here as need to look into the users we have and these argguments etc
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('kitty')

                # request.session['username'] = user.username
                # return redirect('climate')
            
            else:
                # will display this message in html

                messages.info(request, "Username OR password is incorrect")
                # messages.success(request, ("There was an error logging in. Please try again"))
                return redirect('loginPage')

        return render(request, 'authenticate/login.html', {})


def logout_user(request):
    # this method fully logs the user out
    # will need to have this in html as a link to logout page so we can logout - note the name is 'logoutPage' for link and can dipslay username with {{request.user}}
    logout(request)
    return redirect('loginPage')


# I have chnaged to above as automatically checks for duplicates etc
# i will work on cutomising it to our needs :))

#remianing notes from deletion:
# b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
