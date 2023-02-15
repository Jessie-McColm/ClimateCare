from django.urls import path

from . import views

urlpatterns = [
    path('', views.kitty, name='kitty'),
    path('articles',views.articles,name='articles'),
]
