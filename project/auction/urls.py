from django.urls import path 
from .views import *

urlpatterns = [
    path('', route, name ="route"),
    path('md/', mdPage, name ="mdPage"),
    path('login/', loginPage, name ="loginPage"),
    path('register/', registerPage, name ="registerPage"),
    path('home/', homePage, name ="homePage"),
    path('viewLot/', viewLotPage, name ="viewLotPage"),
    path('logout/', logoutPage, name ="logoutPage"),
    path('changePassword/', changePasswordPage, name ="changePasswordPage"),
    
    path('comment/<str:module>/<int:id>/', commentPage, name ="commentPage"),
    
    path('condition/', conditionPage, name ="conditionPage"),
    path('condition/add/', conditionAddPage, name ="conditionAddPage"),
    path('condition/edit/<int:id>/', conditionEditPage, name ="conditionEditPage"),
    
    path('category/', categoryPage, name ="categoryPage"),
    path('category/add/', categoryAddPage, name ="categoryAddPage"),
    path('category/edit/<int:id>/', categoryEditPage, name ="categoryEditPage"),
]
               