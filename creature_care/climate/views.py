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
from django.core.exceptions import ObjectDoesNotExist

from users.decorators import game_master
from .models import Profile, Advice, LocationBin, LocationFountain, Item, Colour, Wearing


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
        Jessie, Laurie, Nevan

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

    eye_colour_obj = cat_data.eye_colour
    eye_colour = eye_colour_obj.colour_hex_val

    fur_colour_obj = cat_data.fur_colour
    fur_colour = fur_colour_obj.colour_hex_val

    time_limit = 3600
    # ----------------------------------------------------------------------------------

    # calculating the time difference to determine how stinky/thirsty/ etc. the kitty is
    # better to calculate each time we send page cause changes depending on current time
    current_time = timezone.now()
    three_days = 259200
    info = {
        'watered': False,
        'cleaned': False,
        'fed': False,
        'fur_colour': fur_colour,
        'eye_colour': eye_colour,
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
            # check that a certain amount of time has passed since the user last tried to water
            water_time_difference = current_time - cat_data.last_thirst_refill
            water_time_difference_seconds = water_time_difference.total_seconds()
            if water_time_difference_seconds > time_limit:
                near_water = validate_location(coordinates, task)
                if near_water:
                    info['task'] = 'water'
                    cat_data.last_thirst_refill = current_time
                    cat_data.save()
                    user_prof.points = user_prof.points + 5
                    user_prof.num_times_watered = user_prof.num_times_watered + 1
                    user_prof.save()

        elif task == "litter":
            litter_time_difference = current_time - cat_data.last_litter_refill
            litter_time_difference_seconds = litter_time_difference.total_seconds()
            if litter_time_difference_seconds > time_limit:
                near_bin = validate_location(coordinates, task)
                if near_bin:
                    info['task'] = 'clean'
                    cat_data.last_litter_refill = current_time
                    cat_data.save()
                    user_prof.points = user_prof.points + 3
                    user_prof.num_times_litter_cleared = user_prof.num_times_litter_cleared + 1
                    user_prof.save()

        elif task == "feed":
            food_time_difference = current_time - cat_data.last_food_refill
            food_time_difference_seconds = food_time_difference.total_seconds()
            if food_time_difference_seconds > time_limit:
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


@login_required(login_url='loginPage')
def leaderboard_page(request):
    """
    Displays a leaderboard

    Authors: Lucia, Laurie

    Returns:
        A http response.
    """

    leaderboard_data = return_leaderboard()  # returns a list of dictionaries for
    # rendering the full leaderboard
    user_rank = return_ranking(request.user.username)  # returns the current user's rank
    return render(request, 'leaderboard.html', {'data': leaderboard_data, 'rank':user_rank})


@login_required(login_url='loginPage')
def my_stats_page(request):
    """
    Displays a stats page on the users progress in the game

    Authors:
        Lucia

    Returns:
        A http response.
    """

    # obtain user data
    user_obj = request.user
    user_prof = Profile.objects.get(user=user_obj)
    username = user_obj.get_username()
    # cat_data = user_prof.creature

    bottle_num = user_prof.num_times_watered
    article_num = user_prof.num_times_fed
    recycle_num = user_prof.num_times_litter_cleared

    info = {
        'username': username,
        'bottle_num': bottle_num,
        'article_num': article_num,
        'recycle_num': recycle_num,
    }

    return render(request, 'my_stats.html', info)


@login_required(login_url='loginPage')
def item_shop_page(request):
    """
    This function handles POST requests from the item shop, and provides functionality
    for allowing users to purchase new items and equip their cat with these items.

    Authors:
        Nevan

    Returns:
        A http response.
    """

    user_obj = request.user
    username = user_obj.get_username()
    user_prof = Profile.objects.get(user=user_obj)
    user_cat = user_prof.creature

    try:
        wearing = Wearing.objects.get(creature=user_cat)
    except ObjectDoesNotExist:
        wearing = Wearing.objects.create(creature=user_cat)

    points_available = user_prof.points

    items = Item.objects.all()
    item_ids = ','.join(str(item.item_id) for item in items)
    item_prices = ','.join(str(item.item_cost) for item in items)

    attempted_purchase = "false"
    successful_purchase = "false"

    info = {
        'username': username,
        'points_available': points_available,
        'item_ids': item_ids,
        'item_prices': item_prices,
        'attempted_purchase': attempted_purchase,
        'successful_purchase': successful_purchase
    }

    if request.method == "POST":
        if request.POST.get('purchase_new_item') == "true":
            attempted_purchase = "true"
            item_id = request.POST.get('item_id')
            item = Item.objects.get(item_id=item_id)
            item_cost = item.item_cost

            if points_available > item_cost:
                user_prof.points = points_available - item_cost
                wearing.item = item

                user_prof.save()
                wearing.save()

                successful_purchase = "true"

            else:
                successful_purchase = "false"

            info['attempted_purchase'] = attempted_purchase
            info['successful_purchase'] = successful_purchase

    return render(request, 'item_shop.html', info)

@login_required(login_url='loginPage')
def colour_shop_page(request):
    """
    This function handles POST requests from the colours shop, and provides functionality
    for allowing users to purchase new items and stylize their cat with these new colours.

    Authors:
        Nevan

    Returns:
        A http response.
    """

    user_obj = request.user
    username = user_obj.get_username()
    user_prof = Profile.objects.get(user=user_obj)
    points_available = user_prof.points
    cat_obj = user_prof.creature

    colours = Colour.objects.all()
    colour_ids = ','.join(str(colour.colour_id) for colour in colours)
    colour_hexs = ','.join(str(colour.colour_hex_val) for colour in colours)
    colour_prices = ','.join(str(colour.colour_cost) for colour in colours)

    attempted_purchase = "false"
    successful_purchase = "false"

    info = {
        'username': username,
        'points_available': points_available,
        'colour_ids': colour_ids,
        'colour_hexs': colour_hexs,
        'colour_prices': colour_prices,
        'attempted_purchase': attempted_purchase,
        'successful_purchase': successful_purchase
    }

    if request.method == "POST":
        if request.POST.get('purchase_new_colour') == "true":
            attempted_purchase = "true"
            colour_id = request.POST.get('colour_id')
            colour_obj = Colour.objects.get(colour_id=colour_id)
            colour_cost = colour_obj.colour_cost

            if points_available > colour_cost:
                user_prof.points = points_available - colour_cost
                if request.POST.get('eye_colour') == "true":
                    cat_obj.eye_colour = colour_id
                elif request.POST.get('fur_colour') == "true":
                    cat_obj.fur_colour = colour_id

                user_prof.save()
                cat_obj.save()

                successful_purchase = "true"

            else:
                successful_purchase = "false"

            info['attempted_purchase'] = attempted_purchase
            info['successful_purchase'] = successful_purchase

    return render(request, 'colour_shop.html', info)


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
    # may need to look into preventing XSS
    if request.method == "POST":
        link_or_content = request.POST.get('link_or_content')
        if link_or_content == "link":
            link = request.POST.get('content')
            source = request.POST.get('source')
            Advice.objects.create(link=link, source=source)
        elif link_or_content == "content":
            content = request.POST.get('content')
            source = request.POST.get('source')
            Advice.objects.create(content=content, source=source)

    return render(request, 'temp_game_master.html')


def page_not_found_view(request, exception):
    """
    Redirects the user to the notFound.html page if they enter an invalid URL.

    Authors:
        Lucia

    Args:
        request(HTTP request): the http request send by a front end client viewing the url
        exception: the exception raised when unable to find a page.
    Returns:
        render(request, 'notFound.html', status=404) renders the template 'cat.html'
    """
    return render(request, 'notFound.html', status=404)


# ---------Below this are functions for views, not views ----------------


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
        user_loc (tuple): tuple of user location (latitude, longitude)
        object_loc (tuple): tuple of object location (latitude, longitude)
        m_dist (float CHECK): maximum desired distance between objects

    Returns:
        in_range (Bool): whether in range of not
    """

    # using haversine distance not euclidean

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


def validate_location(coordinates, location_type):
    """
    Verifies whether the user is near a bin/fountain location by performing calculations based on
    the user's geolocation and the location data stored on bins/fountains.

    Authors:
        Laurie, Jessie, and Nevan

    Args:
        coordinates: The user's coordinates to be validated
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


'''
Retrieves up to the top 20 players in terms of lifetime points

Authors: Laurie

Args: None

Returns: a list of dictionaries, each dictionary represents
an entry in the leaderboards.
'''


def return_leaderboard():
    leaderboard_output = []  # this is the output data, a list of dictionaries
    max_items = len(list(Profile.objects.all()))
    if max_items > 20:  # ensures no more than 20 items are retrieved
        max_items = 20

    # retrieves the first (up to or below) 20 objects of an already ordered database
    top_profiles = list(Profile.objects.all())[0:max_items]

    for i in top_profiles:
        username = i.user.username
        points = i.points
        creature_colour = i.creature.colour
        temp_dictionary = {
            "username": username,
            "points": points,
            "creature": creature_colour
        }
        leaderboard_output.append(temp_dictionary)
    return leaderboard_output

'''
Simple linear search algorithm to find the user's place in the profile's database.

Authors: Laurie

Args: the User object of the user that has logged into the system

Returns: the user's rank, starting at 1 and moving upwards.
'''
def return_ranking(username_required):
    all_profiles = list(Profile.objects.all())
    user_found = False
    search_count = 0
    while (user_found == False) and (search_count < len(all_profiles)):
        if all_profiles[search_count].user.username == username_required:
            user_found = True
        search_count = search_count + 1
    return search_count
