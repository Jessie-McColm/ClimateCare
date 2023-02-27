from django.urls import path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name="loginPage"),
    path('register_user', views.register_user, name="registerPage"),
    path('logout_user', views.logout_user, name="logoutPage"),
    path('activate/<uidb64>/<token>', views.activate, name='activate')
]