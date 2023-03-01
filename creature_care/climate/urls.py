from django.urls import path

from . import views

urlpatterns = [
    path('kitty', views.kitty, name='kitty'),
    path('kitty/<str:type_of>', views.kitty, name='kitty'),
    path('game_masters',views.game_master_page, name='game_masters')
]

# path('articles',views.articles,name='articles') <-- to be added later if needed

handler404="climate.views.page_not_found_view"
