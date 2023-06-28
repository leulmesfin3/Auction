from django.urls import path 
from .views import *

urlpatterns = [
    path('', route, name ="route"),
    path('md/', mdPage, name ="mdPage"),
    path('login/', loginPage, name ="loginPage"),
    path('register/', registerPage, name ="registerPage"),
    path('home/', homePage, name ="homePage"),
    path('viewLot/<int:id>/', viewLotPage, name ="viewLotPage"),
    path('logout/', logoutPage, name ="logoutPage"),
    path('changePassword/', changePasswordPage, name ="changePasswordPage"),
    path('editProfile/', editProfilePage, name ="editProfilePage"),
    
    path('comment/<str:module>/<int:id>/', commentPage, name ="commentPage"),
    
    path('condition/', conditionPage, name ="conditionPage"),
    path('condition/add/', conditionAddPage, name ="conditionAddPage"),
    path('condition/edit/<int:id>/', conditionEditPage, name ="conditionEditPage"),
    
    path('status/', statusPage, name ="statusPage"),
    path('status/add/', statusAddPage, name ="statusAddPage"),
    path('status/edit/<int:id>/', statusEditPage, name ="statusEditPage"),
    
    path('category/', categoryPage, name ="categoryPage"),
    path('category/add/', categoryAddPage, name ="categoryAddPage"),
    path('category/edit/<int:id>/', categoryEditPage, name ="categoryEditPage"),
    
    path('item/', itemPage, name ="itemPage"),
    path('item/add/', itemAddPage, name ="itemAddPage"),
    path('item/edit/<int:id>/', itemEditPage, name ="itemEditPage"),
    
    path('itemMyBid/', itemMyBidPage, name ="itemMyBidPage"),
]
               