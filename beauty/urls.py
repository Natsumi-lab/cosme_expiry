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
    # path('items/', views.item_list, name='item_list'),  # 後で実装
]