"""
This is the django view for the user registration, login, and logout functionality stemming from
/users/.

Authors:
    Lucia
"""


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from climate.models import Profile, Creature

from .forms import CreateUserForm
from .decorators import unauthenticated_user

@unauthenticated_user
def register_user(request):
    """
    The registration page of the project, accessed using /users/register_user. Allows new
    users to create a new user account with their chosen username and password. Only creates
    users in 'player' group.

    Authors:
        Lucia

    Args:
        request(HTTP request): the http request send by a front end client viewing the url 

    Returns:
        render(request, 'authenticate/register.html', context): renders the template
        'register.html' with the context variables stored in the dictionary called context.
        This will display the registration page to the user if a request other than POST
        is sent to the page or if the user didn't send valid information to create an
        account with.

        redirect('loginPage'): redirects the user to the login page after they have
        successfully created a new account
    """

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Account was created for " + username)

            # default adds user to Player group
            group = Group.objects.get(name='Player')
            user.groups.add(group)
            # -------------------
            # creates a creature and a profile for the user
            user_obj = User.objects.get(username=username)
            user_creature = Creature()
            profile = Profile(user=user_obj, creature=user_creature)
            user_creature.save()
            profile.save()
            # ------------------

            return redirect('loginPage')

    context = {'form': form}
    return render(request, 'authenticate/register.html', context)

@unauthenticated_user
def login_user(request):

    """
    This method logs the user in if the correct credentials have been sent via a POST
    request. It can be accessed via /users/login_user

    Authors:
        Lucia

     Args:
        request(HTTP request): the http request send by a front end client viewing the url 

    Returns:
        redirect('loginPage'): redirects the user to the login page if they provided incorrect
        credentials redirect('kitty'): redirects the user to the kitty (climate/) page if they
        provided correct credentials and been successfully logged in
        render(request, 'authenticate/login.html', {}): renders the template 'login.html'. This
        will display the login page to the user if a request other than POST is sent to the page
        and allows them to enter their details into a html form
    """
    
    if request.method == "POST":
        # name passing in from the html name field
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('kitty')

        # will display this message in html
        messages.info(request, "Username OR password is incorrect")
        return redirect('loginPage')

    return render(request, 'authenticate/login.html', {})


def logout_user(request):
    """
    This method fully logs the user out. It can be accessed via /users/logout_user

    Authors:
        Lucia

     Args:
        request(HTTP request): the http request send by a front end client viewing the url 

    Returns:
        redirect('loginPage'): redirects the user to the login page after they have successfully
         logged out
    """
    
    logout(request)
    return redirect('loginPage')
