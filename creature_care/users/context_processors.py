from .decorators import is_dev_or_gm

"""
This will return whether a user is a developer or game master
It is called in settings.py as a context processor
"""
def dev_or_gm_context(request):

    dev_or_gm_bool = is_dev_or_gm(request)

    return {
        'dev_or_gm_bool': dev_or_gm_bool
    }