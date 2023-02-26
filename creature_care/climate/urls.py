from django.urls import path

from . import views

urlpatterns = [
    path('', views.kitty, name='kitty'),
    path('articles',views.articles,name='articles'),
    path('game_masters',views.game_master_page, name='game_masters')
]

handler404="climate.views.page_not_found_view"