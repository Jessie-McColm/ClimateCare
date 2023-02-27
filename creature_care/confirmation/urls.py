from django.urls import path

import views

urlpatterns = [
    path('', views.confirmation, name='kitty'),
]

handler404 = "climate.views.page_not_found_view"
