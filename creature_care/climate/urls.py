from django.urls import path

from . import views

urlpatterns = [
    path('kitty', views.kitty, name='kitty'),
    path('kitty/<str:type_of>', views.kitty, name='kitty'),
    path('my_stats', views.my_stats_page, name='my_stats'),
    path('item_shop', views.item_shop_page, name='item_shop'),
    path('colour_shop', views.colour_shop_page, name='colour_shop'),
    path('leaderboard', views.leaderboard_page, name='leaderboard'),
    path('game_masters', views.game_master_page, name='game_masters'),
]

# path('articles',views.articles,name='articles') <-- to be added later if needed

handler404 = "climate.views.page_not_found_view"
