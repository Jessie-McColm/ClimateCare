from django.contrib import admin

from .models import Creature
from .models import Profile
from .models import Item
from .models import Wearing
from .models import Advice

admin.site.register(Creature)
admin.site.register(Profile)
admin.site.register(Item)
admin.site.register(Wearing)
admin.site.register(Advice)