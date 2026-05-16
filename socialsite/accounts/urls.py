from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='accounts_login'),
    path('signup/', views.signup_view, name='accounts_signup'),
    path('logout/', views.logout_view, name='accounts_logout'),
    path('profile/', views.profile_view, name='accounts_profile'),
    path('activate/<uuid:token>/', views.activate_view, name='activate'),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
]
