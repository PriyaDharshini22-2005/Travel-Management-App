from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('trip_planner/', views.trip_planner, name='trip_planner'),
    path('logout/', views.logout, name='logout'),  
    path('hotels/', views.hotels, name='hotels'),
    path('places/', views.places, name='places'),
    path('expenses/', views.expenses, name='expenses'),
    path('profile/', views.profile_page, name='profile'),
    path('filter-hotels/', views.filter_hotels, name='filter_hotels'),
   

]