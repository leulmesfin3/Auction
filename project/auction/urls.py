from django.urls import path 
from .views import *

urlpatterns = [
    path('', route, name ="route"),
    path('md/', mdPage, name ="mdPage"),
    path('login/', loginPage, name ="loginPage"),
    path('home/', homePage, name ="homePage"),
    path('viewLot/', viewLotPage, name ="viewLotPage"),
    path('logout/', logoutPage, name ="logoutPage"),
]
               