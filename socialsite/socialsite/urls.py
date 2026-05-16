from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from accounts import views as accounts_views
from accounts.admin_views import admin_dashboard
from posts import views as posts_views


# Language switching endpoint (without i18n prefix)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Main URL patterns with i18n support (language prefix)
urlpatterns += i18n_patterns(
    path('', accounts_views.login_view, name='index'),
    path('feed/', posts_views.feed_view, name='feed'),
    path('search/', accounts_views.search_view, name='search'),
    path('admin/', admin.site.urls),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('accounts/', include('accounts.urls')),
    path('login/', accounts_views.login_view, name='login'),
    path('signup/', accounts_views.signup_view, name='signup'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('profile/edit/', accounts_views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', accounts_views.profile_view, name='profile'),
    path('profile/', accounts_views.profile_view, name='own_profile'),
    
    # Follow API endpoints
    path('api/accounts/<str:username>/follow/', accounts_views.follow_user, name='follow_user'),
    path('api/accounts/<str:username>/unfollow/', accounts_views.unfollow_user, name='unfollow_user'),
    
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('api/accounts/', include('accounts.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/messages/', include('messaging.urls')),
    path('messages/', include('chat.urls')),
    path('notifications/', include('notifs.urls')),
)

# Admin site customization
admin.site.site_header = "🎨 Social Media Admin Panel"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Hoş Geldiniz - Yönetim Paneli"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
