from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import EmailVerificationToken, Profile, Follow


# User Admin'i özelleştir
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'
    fields = ('avatar', 'bio', 'birth_date', 'website', 'location')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'avatar_preview', 'post_count', 'follower_count', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def avatar_preview(self, obj):
        try:
            if obj.profile.avatar:
                return format_html(
                    '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                    obj.profile.avatar.url
                )
        except:
            pass
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{}</div>',
            obj.username[0].upper()
        )
    avatar_preview.short_description = '👤 Avatar'
    
    def post_count(self, obj):
        count = obj.posts.count()
        if count > 10:
            return format_html('<span style="color: green; font-weight: bold;">📝 {}</span>', count)
        return format_html('<span>📝 {}</span>', count)
    post_count.short_description = 'Gönderi'
    
    def follower_count(self, obj):
        count = obj.followers.count()
        if count > 50:
            return format_html('<span style="color: purple; font-weight: bold;">⭐ {}</span>', count)
        elif count > 10:
            return format_html('<span style="color: blue; font-weight: bold;">👥 {}</span>', count)
        return format_html('<span>👥 {}</span>', count)
    follower_count.short_description = 'Takipçi'


# User Admin'i yeniden kaydet
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_preview', 'location', 'website', 'follower_count', 'following_count', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{}</div>',
            obj.user.username[0].upper()
        )
    avatar_preview.short_description = '👤 Avatar'
    
    def follower_count(self, obj):
        return format_html('<span style="color: purple; font-weight: bold;">👥 {}</span>', obj.get_followers_count())
    follower_count.short_description = 'Takipçi'
    
    def following_count(self, obj):
        return format_html('<span style="color: blue; font-weight: bold;">👤 {}</span>', obj.get_following_count())
    following_count.short_description = 'Takip'
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user',)
        }),
        ('Profil Detayları', {
            'fields': ('bio', 'avatar', 'birth_date', 'website', 'location')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower_with_avatar', 'arrow', 'following_with_avatar', 'created_at']
    search_fields = ['follower__username', 'following__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def follower_with_avatar(self, obj):
        try:
            if obj.follower.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.follower.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.follower.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}<strong>{}</strong>', avatar, obj.follower.username)
    follower_with_avatar.short_description = '👤 Takipçi'
    
    def following_with_avatar(self, obj):
        try:
            if obj.following.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.following.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.following.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}<strong>{}</strong>', avatar, obj.following.username)
    following_with_avatar.short_description = '⭐ Takip Edilen'
    
    def arrow(self, obj):
        return format_html('<span style="color: #999;">→</span>')
    arrow.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('follower', 'following')
