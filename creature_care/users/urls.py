from django.urls import path
from . import views

"""
These are URL patterns for the user/ directory.

Authors:
    Lucia
"""

urlpatterns = [
    path('login_user', views.login_user, name="loginPage"),
    path('register_user', views.register_user, name="registerPage"),
    path('logout_user', views.logout_user, name="logoutPage"),
]