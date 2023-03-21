from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    """
Writing decorators for authentication to use in views

Authors:
    Lucia
"""
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('kitty')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func



def allowed_users(allowed_roles=[]):
    """
Authors:
    Lucia
"""
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            #print("working")
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("Become a game master to access!")
        
        return wrapper_func
    
    return decorator



def game_master(view_func):
    """

Authors:
    Lucia
"""   
    def wrapper_func(request, *args, **kwargs):
        
        if is_dev_or_gm(request):
                return view_func(request, *args, **kwargs)
        else:
            return redirect('kitty')
    
    return wrapper_func



def is_dev_or_gm(request):
    """

Authors:
    Lucia
"""
    group = None

    if request.user.groups.exists():
        groups = request.user.groups.all()

        for group in groups:
            group_name = group.name
            print(group_name)

            if ("Game_master" == group_name) or (("Developers" == group_name)) :
                return True
        
    return False
