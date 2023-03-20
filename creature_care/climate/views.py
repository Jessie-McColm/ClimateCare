"""
This is the django view for the main page, and handles user interaction with the Kitty
"""
import random
import re

import haversine as hs
from haversine import Unit

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from users.decorators import game_master
from .models import Profile, Advice, LocationBin, LocationFountain, Wearing, Item, Colour
import random



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
        Jessie, Laurie, Nevan, Lucia

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

    colours = cat_colours(cat_data)
    
    time_limit = 300
    # ----------------------------------------------------------------------------------

    # calculating the time difference to determine how stinky/thirsty/ etc the kitty is
    # better to calculate each time we send page cause changes depending on current time
    current_time = timezone.now()
    three_days = 259200
    info = {
        'watered': False,
        'cleaned': False,
        'fed': False,
        'fur_colour': colours["fur_colour"],
        'eye_colour': colours["eye_colour"],
        'cat_item': colours["cat_item"],
        'cat_item_scale': colours['cat_item_scale'],
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
            #check that a certain amount of time has passed since the user last tried to water
            water_time_difference = current_time - cat_data.last_thirst_refill
            water_time_difference_seconds = water_time_difference.total_seconds()
            if water_time_difference_seconds >time_limit:
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
            if litter_time_difference_seconds >time_limit:
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
            if food_time_difference_seconds >time_limit:
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

    if user_prof.paused == True:
        current_time = user_prof.pause_time
    else:
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

    leaderboard_data = return_leaderboard() #returns a list of dictionaries for
    #rendering the full leaderboard
    user_rank = return_ranking(request.user.username)
    return render(request, 'leaderboard.html', {'data':leaderboard_data, 'rank':user_rank})


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

    cat_obj = user_prof.creature

    # gets users cat colours
    colours = cat_colours(cat_obj)

    bottle_num = user_prof.num_times_watered
    article_num = user_prof.num_times_fed
    recycle_num = user_prof.num_times_litter_cleared

    info = {
        'username': username,
        'bottle_num': bottle_num,
        'article_num': article_num,
        'recycle_num': recycle_num,
        'fur_colour': colours["fur_colour"],
        'eye_colour': colours["eye_colour"],
        'cat_item': colours["cat_item"],
        'cat_item_scale': colours['cat_item_scale'],
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
    cat_obj = user_prof.creature

    try:
        wearing = Wearing.objects.get(creature=cat_obj)
    except ObjectDoesNotExist:
        wearing = Wearing.objects.create(creature=cat_obj)

    wearing_item_obj = wearing.item
    if not wearing_item_obj:
        currently_wearing_id = '0'  # denotes that the cat is not wearing anything
        currently_wearing_scale = '0'
    else:
        currently_wearing_id = wearing.item.item_id
        currently_wearing_id = str(currently_wearing_id)
        currently_wearing_scale = wearing.item.scale

    points_available = user_prof.points

    items = Item.objects.all()
    rand_items = random.sample(list(items), k=3)

    rand_item_1 = rand_items[0]
    rand_item_2 = rand_items[1]
    rand_item_3 = rand_items[2]

    item_id_1 = rand_item_1.item_id
    item_id_2 = rand_item_2.item_id
    item_id_3 = rand_item_3.item_id

    print("Item IDs: " + str(item_id_1) + ", " + str(item_id_2) + ", " + str(item_id_3))

    item_price_1 = rand_item_1.item_cost
    item_price_2 = rand_item_2.item_cost
    item_price_3 = rand_item_3.item_cost

    item_scale_1 = rand_item_1.scale
    item_scale_2 = rand_item_2.scale
    item_scale_3 = rand_item_3.scale

    attempted_purchase = "false"
    successful_purchase = "false"

    cat_fur_colour_obj = cat_obj.fur_colour
    cat_eye_colour_obj = cat_obj.eye_colour

    cat_fur_colour = cat_fur_colour_obj.colour_hex_val
    cat_fur_colour += ","
    cat_fur_colour += cat_fur_colour_obj.colour_hex_val_patch

    cat_eye_colour = cat_eye_colour_obj.colour_hex_val

    info = {
        'username': username,
        'points_available': points_available,
        'fur_colour': cat_fur_colour,
        'eye_colour': cat_eye_colour,
        'cat_item': currently_wearing_id,
        'cat_item_scale': currently_wearing_scale,
        'item_id_1': item_id_1,
        'item_price_1': item_price_1,
        'item_scale_1': item_scale_1,
        'item_id_2': item_id_2,
        'item_price_2': item_price_2,
        'item_scale_2': item_scale_2,
        'item_id_3': item_id_3,
        'item_price_3': item_price_3,
        'item_scale_3': item_scale_3,
        'attempted_purchase': attempted_purchase,
        'successful_purchase': successful_purchase
    }

    if request.method == "POST":
        if request.POST.get('purchase_new_item') == "true":
            attempted_purchase = "true"
            item_id = request.POST.get('item_id')

            if item_id != '0':
                item = Item.objects.get(item_id=item_id)
                item_cost = item.item_cost

                if points_available >= item_cost:
                    user_prof.points = points_available - item_cost
                    wearing.item = item

                    user_prof.save()
                    wearing.save()

                    successful_purchase = "true"

                else:
                    successful_purchase = "false"
            else:
                wearing.item = None
                user_prof.save()
                wearing.save()

    wearing_item_obj = wearing.item
    if not wearing_item_obj:
        currently_wearing_id = '0'
        currently_wearing_scale = '0'
    else:
        currently_wearing_id = wearing.item.item_id
        currently_wearing_id = str(currently_wearing_id)
        currently_wearing_scale = wearing.item.scale

    info['cat_item'] = currently_wearing_id
    info['cat_item_scale'] = currently_wearing_scale
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

    attempted_purchase = "false"
    successful_purchase = "false"

    info = {
        'username': username,
        'points_available': points_available,
        'fur_colour': "",
        'eye_colour': "",
        'attempted_purchase': attempted_purchase,
        'successful_purchase': successful_purchase
    }

    print(request.method)

    if request.method == "POST":

        print("Method is POST...")
        print("purchase_new_colour_eyes == " + request.POST.get('purchase_new_colour_eyes'))
        print("purchase_new_colour_fur == " + request.POST.get('purchase_new_colour_fur'))

        if request.POST.get('purchase_new_colour_fur') == "true":
            attempted_purchase = "true"
            if points_available >= 10:
                successful_purchase = "true"
                print("purchase_new_fur_colour == true...")
                colour_hex_str = request.POST.get('fur_colour')
                print("fur_colour retrieved...")
                colour_hexs = colour_hex_str.split(",")
                print("colour_hex_val is " + colour_hexs[0] + "...")
                if colour_hexs[1] == "":
                    print("colour_hex_val_patch is empty...")
                else:
                    print("colour_hex_val_patch is " + colour_hexs[1] + "...")
                colour_obj = Colour.objects.get(
                    colour_hex_val=colour_hexs[0],
                    colour_hex_val_patch=colour_hexs[1]
                )
                cat_obj.fur_colour = colour_obj
                cat_obj.save(update_fields=['fur_colour'])
                print("Fur colour saved!")
                user_prof.points -= 10
                user_prof.save(update_fields=['points'])
                print("Points updated!")

            else:
                successful_purchase = "false"

        if request.POST.get('purchase_new_colour_eyes') == "true":
            print("purchase_new_colour_eyes == true...")
            attempted_purchase = "true"
            if points_available >= 10:
                successful_purchase = "true"
                print("purchase_new_colour_eyes == true...")
                colour_hex_str = request.POST.get('eye_colour')
                print("eye_colour retrieved...")
                colour_hexs = colour_hex_str.split(",")
                print("colour_hex_val is " + colour_hexs[0] + "...")
                colour_obj = Colour.objects.get(
                    colour_hex_val=colour_hexs[0]
                )
                cat_obj.eye_colour = colour_obj
                cat_obj.save(update_fields=['eye_colour'])
                print("Eye colour saved!")
                user_prof.points -= 10
                user_prof.save(update_fields=['points'])
                print("Points updated!")

            else:
                successful_purchase = "false"

    cat_fur_colour_obj = cat_obj.fur_colour
    cat_eye_colour_obj = cat_obj.eye_colour

    cat_fur_colour = cat_fur_colour_obj.colour_hex_val
    cat_fur_colour += ","
    cat_fur_colour += cat_fur_colour_obj.colour_hex_val_patch

    cat_eye_colour = cat_eye_colour_obj.colour_hex_val

    info['fur_colour'] = cat_fur_colour
    info['eye_colour'] = cat_eye_colour

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
    #may need to look into preventing XSS
    if request.method == "POST":
        link_or_content=request.POST.get('link_or_content')
        if link_or_content=="link":
            link=request.POST.get('content')
            source=request.POST.get('source')
            Advice.objects.create(link=link, source=source)
        elif link_or_content=="content":
            content=request.POST.get('content')
            source=request.POST.get('source')
            Advice.objects.create(content=content, source=source)


    return render(request, 'temp_game_master.html')


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

@login_required(login_url='loginPage')
def friend(request, username="none"):
    """
    Shows a random user's kitty if no username is provided in the URL. If a username is provided in the URL, shows that user's kitty

    Authors:
        Jessie, Lucia

    Args:
        request(HTTP request): the http request send by a front end client viewing the url
        username(string): the username provided in the ULR
    Returns:
        render(request, 'friends.html', context)
    """
    user_obj = request.user
    user_prof = Profile.objects.get(user=user_obj)
    cat_obj = user_prof.creature

    colours = cat_colours(cat_obj)
    
    context = {
            "username": user_obj.get_username(),
            'fur_colour': colours["fur_colour"],
            'eye_colour': colours["eye_colour"],
            'cat_item': colours["cat_item"],
            'cat_item_scale': colours['cat_item_scale'],
            "bottle_num": user_prof.num_times_watered,
            "article_num": user_prof.num_times_fed,
            "recycle_num": user_prof.num_times_litter_cleared,
            "friend_username": None,
            "friend_bottle_num": 0,
            "friend_article_num": 0,
            "friend_recycle_num": 0,
            'f_fur_colour': "#ff0000",
            'f_eye_colour': "#ff0000"
            }


    if username == "none":
        # get a random user from the database
        profiles = list(Profile.objects.filter(private=False).exclude(access_level=3))
        if not user_prof.private and user_prof.access_level != 3:
            profiles.remove(user_prof)
        if len(profiles) == 0:
            return render(request, 'friends.html', context)

        #exclude the current user from possibilities

        choice_range=len(profiles)-1
        choice=random.randint(0, choice_range)
        profile_choice=profiles[choice]
        username = profile_choice.user.username

    else:
        user_choice = User.objects.get(username=username)
        profile_choice=Profile.objects.get(user=user_choice)
        if profile_choice.private or profile_choice.access_level == 3:
            return redirect('friend')

    
    # get freind cat colours
    f_cat_obj = profile_choice.creature
    f_colours = cat_colours(f_cat_obj)
    

    context = {
        "username": user_obj.get_username(),
        'fur_colour': colours["fur_colour"],
        'eye_colour': colours["eye_colour"],
        'cat_item': colours["cat_item"],
        'cat_item_scale': colours['cat_item_scale'],
        "bottle_num": user_prof.num_times_watered,
        "article_num": user_prof.num_times_fed,
        "recycle_num": user_prof.num_times_litter_cleared,
        "friend_username": username,
        "friend_bottle_num": profile_choice.num_times_watered,
        "friend_article_num": profile_choice.num_times_fed,
        "friend_recycle_num": profile_choice.num_times_litter_cleared,
        'f_fur_colour': f_colours["fur_colour"],
        'f_eye_colour': f_colours["eye_colour"],
        'f_cat_item': f_colours["cat_item"],
        'f_cat_item_scale': f_colours['cat_item_scale'],
    }
    
    return render(request, 'friends.html', context)


@login_required(login_url='loginPage')
def settings_page(request):
    #in the request that the request.method is not a post, the button will have to be set to the right value
    #(paused or unpaused)
    user_prof = Profile.objects.get(user=request.user)
    user_obj = request.user
    if request.method == "POST":
        pause_data = request.POST.get('pause_data') #this should be the data retrieved from the post function
        print(pause_data)
        if pause_data == "False": #if the pause button is set to false
            if user_prof.paused == True: #filters for the case where the pause button started at
            #false and the user didn't touch it
                end_pause(user_prof) #ends the pause if the user was previously paused
        elif pause_data == "True": #in the case that pause_data is True, maybe adjust later
            start_pause(user_prof)
        if request.POST.get('current_password') != "": #if the user has attempted to set a new password
            user = authenticate(username=user_obj.username, password=request.POST.get('current_password'))
            if user is not None:
                 #if the user
                #has successfully entered their current password
                if (request.POST.get('new_password')==request.POST.get('new_password2')):
                    user_obj.set_password(request.POST.get('new_password'))
                    user_obj.save()
                else:
                    print("passwords don't match")
            else: #if the user failed to enter their password successfully
                print("Current password entered incorrectly")
        if request.POST.get('current_username') != "": #if the user has set a new username
            user_obj.username = request.POST.get('current_username')
            user_obj.save()
        privacy_setting = request.POST.get('privacy_setting')
        if privacy_setting=="True":
             user_prof.private=True
             user_prof.save()
        else:
            user_prof.private=False
            user_prof.save()

    context={"is_paused":user_prof.paused,"is_private":user_prof.private} #need to change once DB is updated
    return render(request, 'settings.html',context)


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
        user_loc (tuple): tuple of user location (lattitude, longitude)
        object_loc (tuple): tuple of object location (lattitude, longitude)
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


def return_leaderboard():
    '''
    Retrieves up to the top 20 players in terms of lifetime points

    Authors: Laurie

    Args: None

    Returns: a list of dictionaries, each dictionary represents
    an entry in the leaderboards.
    '''
    leaderboard_output = [] #this is the ouput data, a list of dictionaries
    max_items = len(list(Profile.objects.exclude(access_level=3)))
    if max_items > 20: #ensures no more than 20 items are retrieved
        max_items = 20
    top_profiles = list(Profile.objects.exclude(access_level=3))[0:max_items] #retrieves the
    #first (up to or below) 20 objects of an already ordered database
    for i in top_profiles:
        username = (i.user).username
        points = i.points
        creature_eye_colour = i.creature.eye_colour
        creature_fur_colour = i.creature.fur_colour
        temp_dictionary = {
            "username": username,
            "points": points,
            "creature_eye_colour": creature_eye_colour,
            "creature_fur_colour": creature_fur_colour
        }
        leaderboard_output.append(temp_dictionary)
    return leaderboard_output


def return_ranking(username_required):
    '''
    Simple linear search algorithm to find the user's place in the profile's database.

    Authors: Laurie

    Args: the User object of the user that has logged into the system

    Returns: the user's rank, starting at 1 and moving upwards.
    '''
    all_profiles = list(Profile.objects.exclude(access_level=3))
    user_found = False
    search_count = 0
    while (user_found == False) and (search_count < len(all_profiles)):
        if all_profiles[search_count].user.username == username_required:
            user_found = True
        search_count = search_count + 1
    if search_count == len(all_profiles) and user_found == False:
        search_count = 0 #admin user's rank is zero
    return search_count


def start_pause(user_prof):
    '''
    A function to start a pause on a user. The function edits the database to reflect that the user
    has actually paused, and stores when the user paused.

    Authors: Laurie

    Args: the Profile object of the user that is sending the request to start the pause
    '''
    user_prof.paused = True
    user_prof.pause_time = timezone.now()
    user_prof.save()


def end_pause(user_prof):
    '''
    A function to fairly return a user from pause to normal gameplay. This function uses the time
    the user paused and the last time they fed/watered/cleaned their kitty to update the kitty's
    data in a way that reflects how it was left.

    Authors: Laurie

    Args: the Profile object of the user that is sending the request to end the pause
    '''
    user_prof.paused = False
    current_time = timezone.now()
    cat_data = user_prof.creature

    water_time_difference = user_prof.pause_time - cat_data.last_thirst_refill
    cat_data.last_thirst_refill = current_time - water_time_difference

    litter_time_difference = user_prof.pause_time - cat_data.last_litter_refill
    cat_data.last_litter_refill = current_time - litter_time_difference

    food_time_difference = user_prof.pause_time - cat_data.last_food_refill
    cat_data.last_food_refill = current_time - food_time_difference

    cat_data.save()
    user_prof.save()


def cat_colours(cat_data):
    """ 
    This function processes gettign the colours and items from a creature oject so we can pass to the front end 
    
    Authors:
        Lucia

    Returns:
        A context dictionary
    
    """
    

    

    eye_colour_obj = cat_data.eye_colour
    eye_colour = eye_colour_obj.colour_hex_val

    fur_colour_obj = cat_data.fur_colour
    
    fur_colour = fur_colour_obj.colour_hex_val
    fur_colour += ","
    fur_colour += fur_colour_obj.colour_hex_val_patch

    try:
        wearing = Wearing.objects.get(creature=cat_data)
    except ObjectDoesNotExist:
        wearing = Wearing.objects.create(creature=cat_data)

    wearing_item_obj = wearing.item
    if not wearing_item_obj:
        wearing_id = '0'  # denotes that the cat is not wearing anything
        wearing_scale = '0'
    else:
        wearing_id = wearing.item.item_id
        wearing_id = str(wearing_id)
        wearing_scale = wearing.item.scale

    details = {
        'fur_colour': fur_colour,
        'eye_colour': eye_colour,
        'cat_item': wearing_id,
        'cat_item_scale': wearing_scale,
    }

    return details
