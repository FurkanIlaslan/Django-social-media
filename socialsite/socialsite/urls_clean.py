from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from accounts import views as accounts_views


def feed(request):
    return render(request, 'feed.html')


urlpatterns = [
    path('', accounts_views.login_view, name='index'),
    path('feed/', feed, name='feed'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('login/', accounts_views.login_view, name='login'),
    path('signup/', accounts_views.signup_view, name='signup'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('api/accounts/', include('accounts.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/messages/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
