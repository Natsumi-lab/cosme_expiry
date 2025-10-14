from django.urls import path
from . import views

app_name = 'beauty'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('signout/', views.SignOutView.as_view(), name='signout'),
    
    # Items
    path('items/new/', views.item_new, name='item_new'),
    path('items/<int:id>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:id>/', views.item_detail, name='item_detail'),
    path('items/', views.item_list, name='item_list'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    
    # API
    path('api/taxons/', views.api_taxons, name='api_taxons'),
    path('api/notifications/summary/', views.get_notifications_summary, name='notifications_summary'),
    path('api/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]