from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('', views.dashboard, name='dashboard'),
    path('user/', views.user, name='user'),
    path('support/', views.support, name='support'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('subscription/', views.subscription, name='subs'),
]