from django.urls import path
from django.conf.urls import url


from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    path('user/', views.user, name='user'),
    path('support/', views.support, name='support'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('subscription/', views.subscription, name='subs'),
    # url(r'^$', views.Predict, name='blog-home'),
    url(r'^dashboard/model/$',views.data_Predict,name="model"),
]


