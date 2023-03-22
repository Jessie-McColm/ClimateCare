from .decorators import is_dev_or_gm


def dev_or_gm_context(request):
    """
    This will return whether a user is a developer or game master
    It is called in settings.py as a context processor

    Authors:
        Lucia
    """
    dev_or_gm_bool = is_dev_or_gm(request)

    return {
        'dev_or_gm_bool': dev_or_gm_bool
    }