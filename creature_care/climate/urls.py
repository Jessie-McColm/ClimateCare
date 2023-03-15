from django.urls import path

from . import views

urlpatterns = [
    path('kitty', views.kitty, name='kitty'),
    path('kitty/<str:type_of>', views.kitty, name='kitty'),
    path('friend/<str:username>', views.friend, name='friend'),
    path('friend', views.friend, name='friend'),
    path('friend_list', views.add_friend, name='add_friend'),
    path('my_stats',views.my_stats_page, name='my_stats'),
    path('shop',views.shop_page, name='shop'),
    path('item_shop',views.kitty, name='item_shop'),
    path('leaderboard',views.leaderboard_page, name='leaderboard'),
    path('game_masters',views.game_master_page, name='game_masters'),
    path('colour_shop',views.kitty, name='colour_shop'),
    path('settings',views.settings_page,name='settings'),
    
]

# path('articles',views.articles,name='articles') <-- to be added later if needed

handler404="climate.views.page_not_found_view"
