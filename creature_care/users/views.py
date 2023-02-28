from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from climate.models import Profile, Creature

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.forms import UserCreationForm

from .tokens import account_activation_token
from .forms import CreateUserForm
from .decorators import unauthenticated_user


# Create your views here.

# only lets you access if not logged in
@unauthenticated_user
def register_user(request):
    # gets form I have put in forms.py which we can customise later

    print('Registering new user...')

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        print('Registration form created...')
        if form.is_valid():
            print('Form is valid...')
            # makes user :))
            user = form.save(commit=False)
            print('Form saved...')
            user.is_active = False
            print('User set to inactive...')
            user.save()

            # -------------------
            # creates a creature and a profile for the user 
            user_obj = User.objects.get(username=user)
            user_creature = Creature()
            profile = Profile(user=user_obj, creature=user_creature)
            user_creature.save()
            profile.save()
            # ------------------
            print('Profile associated with account...')

            activate_email(request, user, form.cleaned_data.get('email'))

            return redirect('climate/kitty')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    context = {'form': form}
    return render(request, 'authenticate/register.html', context)


def activate_email(request, user, email):
    print('\'activate_email\' function call...')
    mail_subject = 'Activate your user account.'
    message = render_to_string('email/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[email])
    if email.send():
        print('Email sent!')
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{email}</b> inbox and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        print('FAILURE: Email not sent.')
        messages.error(request, f'Problem sending confirmation email to {email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    return redirect('homepage')


@unauthenticated_user
def login_user(request):
    # if user already logged in, redirect to the home kitty page
    # if you go to page and actually do something
    if request.method == "POST":
        # name passing in from the html name field
        # username = request.POST['username'] changed to below
        username = request.POST.get('username')
        password = request.POST.get('password')
        # error here as need to look into the users we have and these arguments etc
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

# remianing notes from deletion:
# b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
