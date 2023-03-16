from django.contrib import admin

from .models import Creature
from .models import Profile
from .models import Item
from .models import Wearing
from .models import Advice
from .models import LocationBin
from .models import LocationFountain
from .models import Colour

admin.site.register(Creature)
admin.site.register(Profile)
admin.site.register(Item)
admin.site.register(Wearing)
admin.site.register(Advice)
admin.site.register(LocationBin)
admin.site.register(LocationFountain)
admin.site.register(Colour)
