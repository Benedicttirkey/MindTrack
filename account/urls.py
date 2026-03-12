
from django.urls import path
from . import views

urlpatterns = [

    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('send_email_captcha/', views.send_email_captcha,name='send_email_captcha'),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('home/', views.home, name='home'),
    path('daily_record/', views.daily_record, name='daily_record'),
    path('daily-record/mood/', views.mood_record, name='mood_record'),
    path('daily-record/lifestyle/', views.lifestyle_record, name='lifestyle_record'),
    path('data-visualizations/', views.data_visualizations, name='data_visualizations'),
    path('profile/', views.profile, name='profile'),

]
