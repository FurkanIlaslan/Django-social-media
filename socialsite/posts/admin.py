from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment, Like, Report


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author_with_avatar', 'image_preview', 'content_preview', 'likes_badge', 'comments_badge', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def author_with_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.author.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 35px; height: 35px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 14px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.author.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}<strong>{}</strong>', avatar, obj.author.username)
    author_with_avatar.short_description = '👤 Yazar'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">📝 Metin</span>')
    image_preview.short_description = '🖼️ Görsel'
    
    def content_preview(self, obj):
        text = obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
        return format_html('<div style="max-width: 300px;">{}</div>', text)
    content_preview.short_description = '📝 İçerik'
    
    def likes_badge(self, obj):
        count = obj.likes_count
        if count > 100:
            color = 'background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'
        elif count > 50:
            color = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
        elif count > 10:
            color = 'background: #667eea;'
        else:
            color = 'background: #999;'
        return format_html(
            '<span style="{} color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">❤️ {}</span>',
            color, count
        )
    likes_badge.short_description = '❤️ Beğeni'
    
    def comments_badge(self, obj):
        count = obj.comments_count
        if count > 50:
            color = 'background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'
        elif count > 20:
            color = 'background: #11998e;'
        elif count > 5:
            color = 'background: #38ef7d;'
        else:
            color = 'background: #999;'
        return format_html(
            '<span style="{} color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">💬 {}</span>',
            color, count
        )
    comments_badge.short_description = '💬 Yorum'
    
    fieldsets = (
        ('Gönderi Bilgileri', {
            'fields': ('author', 'content', 'image')
        }),
        ('İstatistikler', {
            'fields': ('likes_count', 'comments_count'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_with_avatar', 'post_preview', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def author_with_avatar(self, obj):
        try:
            if obj.author.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.author.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.author.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}<strong>{}</strong>', avatar, obj.author.username)
    author_with_avatar.short_description = '👤 Yazar'
    
    def post_preview(self, obj):
        text = obj.post.content[:40] + '...' if len(obj.post.content) > 40 else obj.post.content
        return format_html('<div style="max-width: 200px; color: #666;">{}</div>', text)
    post_preview.short_description = '📝 Gönderi'
    
    def content_preview(self, obj):
        text = obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
        return format_html('<div style="max-width: 250px;">{}</div>', text)
    content_preview.short_description = '💬 Yorum'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user_with_avatar', 'post_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def user_with_avatar(self, obj):
        try:
            if obj.user.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.user.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.user.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}❤️ <strong>{}</strong>', avatar, obj.user.username)
    user_with_avatar.short_description = '👤 Kullanıcı'
    
    def post_preview(self, obj):
        text = obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
        return format_html('<div style="max-width: 250px;">{}</div>', text)
    post_preview.short_description = '📝 Gönderi'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter_with_avatar', 'reported_item', 'reason_badge', 'status_badge', 'created_at', 'action_buttons')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('reporter__username', 'description', 'moderator_note')
    readonly_fields = ('reporter', 'content_type', 'object_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Rapor Bilgileri', {
            'fields': ('reporter', 'content_type', 'object_id', 'reason', 'description')
        }),
        ('Durum', {
            'fields': ('status', 'moderator', 'moderator_note')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def reporter_with_avatar(self, obj):
        try:
            if obj.reporter.profile.avatar:
                avatar = format_html(
                    '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px;" />',
                    obj.reporter.profile.avatar.url
                )
            else:
                avatar = format_html(
                    '<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; margin-right: 8px;">{}</div>',
                    obj.reporter.username[0].upper()
                )
        except:
            avatar = ''
        return format_html('{}🚨 <strong>{}</strong>', avatar, obj.reporter.username)
    reporter_with_avatar.short_description = '👤 Raporlayan'
    
    def reported_item(self, obj):
        item_display = obj.get_reported_item_display()
        return format_html('<div style="max-width: 300px; font-size: 13px;">{}</div>', item_display)
    reported_item.short_description = '📍 Raporlanan'
    
    def reason_badge(self, obj):
        colors = {
            'spam': '#fbbf24',
            'harassment': '#f97316',
            'hate_speech': '#ef4444',
            'violence': '#dc2626',
            'nudity': '#ec4899',
            'false_info': '#8b5cf6',
            'other': '#6b7280',
        }
        color = colors.get(obj.reason, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap;">{}</span>',
            color,
            obj.get_reason_display()
        )
    reason_badge.short_description = '⚠️ Sebep'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'reviewing': '#3b82f6',
            'approved': '#10b981',
            'rejected': '#6b7280',
        }
        icons = {
            'pending': '⏳',
            'reviewing': '🔍',
            'approved': '✅',
            'rejected': '❌',
        }
        color = colors.get(obj.status, '#6b7280')
        icon = icons.get(obj.status, '')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = '📊 Durum'
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="/admin/posts/report/{}/change/" style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 4px;">İncele</a>',
                obj.id
            )
        return format_html('<span style="color: #999;">-</span>')
    action_buttons.short_description = '⚡ İşlemler'
