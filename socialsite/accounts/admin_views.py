from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from posts.models import Post, Comment, Like
from accounts.models import Follow, Profile
from notifs.models import Notification
import json


@staff_member_required
def admin_dashboard(request):
    """Özel admin dashboard görünümü"""
    
    # Tarih aralıkları
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Genel İstatistikler
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_likes = Like.objects.count()
    
    # Son 7 günün istatistikleri
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_posts_week = Post.objects.filter(created_at__gte=week_ago).count()
    new_comments_week = Comment.objects.filter(created_at__gte=week_ago).count()
    
    # Son 30 günün istatistikleri
    new_users_month = User.objects.filter(date_joined__gte=month_ago).count()
    new_posts_month = Post.objects.filter(created_at__gte=month_ago).count()
    
    # En aktif kullanıcılar (en çok post atan)
    top_posters = User.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:5]
    
    # En popüler postlar (en çok beğenilen)
    # "Like" modelinde post tarafı related_name='post_likes'
    popular_posts = Post.objects.annotate(
        like_count=Count('post_likes')
    ).order_by('-like_count')[:5]
    
    # Son kayıt olan kullanıcılar
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:5]
    
    # Son postlar
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    
    # Günlük aktivite (son 7 gün)
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_start = timezone.datetime.combine(day, timezone.datetime.min.time())
        day_end = timezone.datetime.combine(day, timezone.datetime.max.time())
        
        if timezone.is_aware(day_start):
            day_start = day_start
        else:
            day_start = timezone.make_aware(day_start)
            
        if timezone.is_aware(day_end):
            day_end = day_end
        else:
            day_end = timezone.make_aware(day_end)
        
        daily_stats.append({
            'date': day.strftime('%d %b'),
            'users': User.objects.filter(date_joined__range=[day_start, day_end]).count(),
            'posts': Post.objects.filter(created_at__range=[day_start, day_end]).count(),
            'comments': Comment.objects.filter(created_at__range=[day_start, day_end]).count(),
        })
    
    daily_stats.reverse()  # Eski tarihten yeniye sırala
    
    # Engagement istatistikleri
    avg_likes_per_post = Like.objects.count() / Post.objects.count() if Post.objects.count() > 0 else 0
    avg_comments_per_post = Comment.objects.count() / Post.objects.count() if Post.objects.count() > 0 else 0
    
    # En çok takip edilen kullanıcılar
    top_followed = User.objects.annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]
    
    # JSON formatına dönüştür
    daily_stats_json = json.dumps(daily_stats)
    
    context = {
        # Genel istatistikler
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        
        # Haftalık istatistikler
        'new_users_week': new_users_week,
        'new_posts_week': new_posts_week,
        'new_comments_week': new_comments_week,
        
        # Aylık istatistikler
        'new_users_month': new_users_month,
        'new_posts_month': new_posts_month,
        
        # Listeler
        'top_posters': top_posters,
        'popular_posts': popular_posts,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'top_followed': top_followed,
        
        # Grafik verisi
        'daily_stats': daily_stats_json,
        
        # Engagement
        'avg_likes_per_post': round(avg_likes_per_post, 1),
        'avg_comments_per_post': round(avg_comments_per_post, 1),
    }
    
    return render(request, 'admin/dashboard.html', context)
