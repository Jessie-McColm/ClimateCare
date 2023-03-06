"""
This is the django view for the main page, and handles user interaction with the Kitty
"""
import random
import re

import haversine as hs
from haversine import Unit

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from users.decorators import game_master
from .models import Profile, Advice, LocationBin, LocationFountain


# this decorator means if not logged in sends back to login page
# might want to change in future
@login_required(login_url='loginPage')
# @allowed_users(allowed_roles=['Developers','Game_masters','Player'])
def kitty(request, type_of="none"):
    """
    The main page of the project, accessed using climate/. Displays the creature and shows its
    current state, while providing functionality to feed/water/clean it. Uses geolocation
    functionality to verify whether a user is within a sensible distance from a fountain/bin

    Authors:
        Jessie and Laurie

    Args:
        request(HTTP request): the http request send by a front end client viewing the url
        type_of: Caught from the URL, used to send back article data

    Returns:
        render(request, 'cat.html',info): renders the template 'cat.html' with the context
        variables stored in the dictionary called info

    """

    # -----------------
    # Gets the info you need (in this block for now for clarity)
    # username = request.user.get_username()

    # can also use this: User.objects.get(username = username)
    user_obj = request.user
    user_prof = Profile.objects.get(user=user_obj)
    cat_data = user_prof.creature

    # ----------------------------------------------------------------------------------

    # calculating the time difference to determine how stinky/thirsty/ etc the kitty is
    # better to calculate each time we send page cause changes depending on current time
    current_time = timezone.now()
    three_days = 259200
    info = {
        'watered': False,
        'cleaned': False,
        'fed': False,
        'colour': cat_data.colour,
        'name': cat_data.name,
        'task': "none",
        'message': "",
        'source': "",
        'content': "",
        'thirsty': False,
        'stinky': False,
        'hungry': False
    }

    if request.method == "POST":
        # set null coordinates for feeding
        task = request.POST.get('task')
        coordinates_string = request.POST.get('coordinates')

        # will need testing
        coordinates = string_coord_convert(coordinates_string)

        if task == "water":
            near_water = validate_location(coordinates, cat_data, task)
            if near_water:
                info['task'] = 'water'
                setattr(cat_data, "last_thirst_refill", current_time)
                cat_data.save()
                user_prof.points = user_prof.points + 5
                user_prof.num_times_watered = user_prof.num_times_watered + 1
                user_prof.save()

        elif task == "litter":
            near_bin = validate_location(coordinates, cat_data, task)
            if near_bin:
                info['task'] = 'clean'
                cat_data.last_litter_refill = current_time
                cat_data.save()
                user_prof.points = user_prof.points + 3
                user_prof.num_times_litter_cleared = user_prof.num_times_litter_cleared + 1
                user_prof.save()

        elif task == "feed":
            cat_data.last_food_refill = current_time 
            cat_data.save()
            user_prof.points = user_prof.points + 1
            user_prof.num_times_fed = user_prof.num_times_fed + 1
            user_prof.save()
            # can we play a little animation?
            info['task'] = 'feed'

    # always a get after a post so need to do this
    if type_of == "articles":
        info['fed'] = True
        articles_list = retrieve_advice()
        info['message'] = str(articles_list[0])
        info['content'] = str(articles_list[1])
        info['source'] = str(articles_list[2])

    if type_of == "water":
        info['watered'] = True

    if type_of == "clean":
        info['cleaned'] = True

    current_time = timezone.now()

    water_time_difference = current_time - cat_data.last_thirst_refill
    litter_time_difference = current_time - cat_data.last_litter_refill
    food_time_difference = current_time - cat_data.last_food_refill

    water_time_difference_seconds = water_time_difference.total_seconds()
    litter_time_difference_seconds = litter_time_difference.total_seconds()
    food_time_difference_seconds = food_time_difference.total_seconds()

    if water_time_difference_seconds > three_days:
        info['thirsty'] = True

    elif litter_time_difference_seconds > three_days:
        info['stinky'] = True

    elif food_time_difference_seconds > three_days:
        info['hungry'] = True

    return render(request, 'cat.html', info)


def validate_location(coordinates, cat_data, location_type):
    """
    Verifies whether the user is near a bin/fountain location by performing calculations based on
    the user's geolocation and the location data stored on bins/fountains.

    Authors:
        Laurie, Jessie, and Nevan

    Args:
        coordinates: The user's coordinates to be validated
        cat_data: The cat object representing the user's cat in the database, through which
                  datetime stamps will be updated
        location_type: A string specifying whether the user is near a bin or a water fountain

    Returns:
        A boolean that denotes whether the user is near a location or not
          + True means the user is near a bin/fountain
          - False means the user is NOT near a bin/fountain
    """
    success = False
    location_counter = 0
    if location_type == 'litter':
        num_locations = len(list(LocationBin.objects.all()))
        while (success is False) and (location_counter <= num_locations - 1):
            current_bin = list(LocationBin.objects.all())[location_counter]
            success = within_distance(
                (coordinates[0], coordinates[1]),
                (current_bin.latitude, current_bin.longitude),
                200
            )
            location_counter = location_counter + 1

    elif location_type == 'water':
        num_locations = len(list(LocationFountain.objects.all()))
        while (success is False) and (location_counter <= num_locations - 1):
            # every single location, checking if the user is within distance
            current_fountain = list(LocationFountain.objects.all())[location_counter]
            success = within_distance(
                (coordinates[0], coordinates[1]),
                (current_fountain.latitude, current_fountain.longitude),
                100
            )
            location_counter = location_counter + 1
    if success:  # if a valid location is found, this condition is chosen
        print(coordinates, location_type)
        return True
    print("not within distance")
    return False  # if no valid location is found, this is returned (may need error display)


@login_required(login_url='loginPage')
def leaderboard_page(request):
    """
    Displays a leaderboard

    Authors:
        

    Returns:
        A http response.
    """

    return HttpResponse("You're at the leaderboard page")



@login_required(login_url='loginPage')
def my_stats_page(request):
    """
    Displays a stats page on the users progress in the game

    Authors:
        Lucia

    Returns:
        A http response.
    """
    
    #obtain user data
    user_obj = request.user
    user_prof = Profile.objects.get(user=user_obj)
    username = user_obj.get_username()
    #cat_data = user_prof.creature
    

    bottle_num = user_prof.num_times_watered
    article_num = user_prof.num_times_fed
    recycle_num = user_prof.num_times_litter_cleared

    info = {
        'username': username,
        'bottle_num': bottle_num,
        'article_num': article_num,
        'recycle_num': recycle_num,

    }

    return HttpResponse("You're at the my stats page")



@login_required(login_url='loginPage')
# @allowed_users(allowed_roles=['Developers','Game_masters','Player'])
@game_master
def game_master_page(request): 
    """
    Redirects an authorised user to the game master's page.

    Authors:
        Lucia

    Returns:
        A http response.
    """
    return HttpResponse("You're at the master page")


def page_not_found_view(request, exception):
    """
    Redirects the user to the notFound.html page if they enter an invalid URL.

    Authors:
        Lucia

    Args:
        request(HTTP request): the http request send by a front end client viewing the url
    Returns:
        render(request, 'notFound.html', status=404) renders the template 'cat.html'
    """
    return render(request, 'notFound.html', status=404)



# ---------Below not views but functions for views ----------------


def retrieve_advice():
    """
    This function retrieves a random piece of advice available in the Advice database.

    Authors:
        Laurie

    Returns:
         A list of data, the first item being "link" or "message". This determines
         whether the user will be simply given a link to click or message to read. The second
         item is either 1) the link or 2) the content. The third item is always the source of
         the information.
    """
    random_population = list(Advice.objects.all())
    advice_object = random.choice(random_population)
    content = advice_object.content
    link = advice_object.link
    source = advice_object.source
    if content == "":
        return ["link", link, source]
    return ["message", content, source]


def within_distance(user_loc, object_loc, m_dist):
    """
    Calculates haversine distance (not euclidean) and returns if within distance

    Authors:
        Lucia

    Args:
        user_loc (tuple): tuple of user location (lattitude, longitude)
        object_loc (tuple): tuple of object location (lattitude, longitude)
        m_dist (float CHECK): maximum desired distance between objects

    Returns:
        in_range (Bool): whether in range of not
    """

    # using haversine distance not eulcidean

    # To calculate distance in meters
    o_dist = hs.haversine(user_loc, object_loc, unit=Unit.METERS)

    in_range = bool(o_dist <= m_dist)

    return in_range


def string_coord_convert(coord_string):
    """
    Converts a set of coordinates from a string to a tuple of two floats

    Authors:
        Lucia

    Args:
        coord_string(String): two coordinates separated by a comma

    Returns:
        out(tuple): a tuple of the latitude and longitude as floats
    """

    # sort out grouping as shouldn't have to do below with tuple
    # remove plus symbol if there is one
    coord_string.replace('+', '')
    coord_regex = re.findall(r"((\-?|\+?)?\d+(\.\d+)?)", coord_string)
    coordinates = [coord_regex[0][0], coord_regex[1][0]]
    out = tuple([float(value) for value in coordinates])
    return out
