
from django.urls import path
from . import views

urlpatterns = [
    path('properties/', views.property_list, name='property_list'),
    # path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:property_id>/', views.property_detail, name='property_detail'),
    path('properties/add/', views.property_create, name='property_create'),
    path('properties/sale/add/', views.property_sale_create, name='property_sale_create'),
    path('properties/rental/add/', views.property_rental_create, name='property_rental_create'),
    path('stats/', views.stats, name='stats'),
    path('properties/owner/<int:user_id>/', views.properties_by_owner, name='properties_by_owner'),
    path('properties/tenant/<int:user_id>/', views.properties_by_tenant, name='properties_by_tenant'),
    path('properties/buyer/<int:user_id>/', views.properties_by_buyer, name='properties_by_buyer'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('transactions/', views.transaction_history, name='transaction_history'),

]

