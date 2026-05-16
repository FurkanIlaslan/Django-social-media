from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Exists, OuterRef, Q, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Post, Like, Comment, Report
from accounts.models import Follow
from notifs.utils import create_notification

User = get_user_model()


@login_required
def feed_view(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        
        if not content:
            messages.error(request, 'Post içeriği boş olamaz.')
            return redirect('/feed/')
        
        Post.objects.create(
            author=request.user,
            content=content,
            image=image
        )
        return redirect('/feed/')
    
    # Feed filtresi: 'all' (tüm gönderiler) veya 'following' (sadece takip edilenler)
    feed_filter = request.GET.get('filter', 'all')
    
    # Kullanıcının beğendiği postları kontrol et
    posts_query = Post.objects.select_related('author', 'author__profile').prefetch_related(
        'comments__author', 'comments__author__profile'
    ).annotate(
        user_has_liked=Exists(
            Like.objects.filter(post=OuterRef('pk'), user=request.user)
        )
    )
    
    # Sadece takip edilen kullanıcıların postlarını göster
    if feed_filter == 'following':
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        posts_query = posts_query.filter(
            Q(author__in=following_users) | Q(author=request.user)
        )
    
    # Sayfalama: Her sayfada 10 post
    posts_query = posts_query.order_by('-created_at')
    paginator = Paginator(posts_query, 10)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)
    
    # Kullanıcı önerileri - akıllı algoritma
    # 1. Şu anda takip etmediğin kullanıcılar
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    # 2. Ortak takipçilere göre öneri (takip ettiğin kişilerin takip ettiği kişiler)
    mutual_suggestions = User.objects.filter(
        followers__follower_id__in=following_ids
    ).exclude(
        id=request.user.id
    ).exclude(
        id__in=following_ids
    ).select_related('profile').annotate(
        mutual_count=Count('followers')
    ).order_by('-mutual_count')[:3]
    
    # 3. Eğer ortak takipçi önerisi yetersizse, popüler kullanıcıları öner
    if len(mutual_suggestions) < 3:
        popular_users = User.objects.exclude(
            id=request.user.id
        ).exclude(
            id__in=following_ids
        ).select_related('profile').annotate(
            follower_count=Count('followers')
        ).order_by('-follower_count')[:3]
        
        # Ortak önerileri ve popüler kullanıcıları birleştir
        suggested_users = list(mutual_suggestions) + list(popular_users)
        # Unique yap ve ilk 3'ü al
        seen = set()
        suggested_users = [x for x in suggested_users if not (x.id in seen or seen.add(x.id))][:3]
    else:
        suggested_users = mutual_suggestions
    
    return render(request, 'feed.html', {
        'posts': posts_page,
        'feed_filter': feed_filter,
        'has_next': posts_page.has_next(),
        'next_page': posts_page.next_page_number() if posts_page.has_next() else None,
        'suggested_users': suggested_users,
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # Zaten beğenmişse beğeniyi kaldır
        like.delete()
        post.likes_count -= 1
        post.save()
        
        # Beğeni bildirimini sil
        from notifs.models import Notification
        Notification.objects.filter(
            notification_type='like',
            sender=request.user,
            receiver=post.author,
            post=post
        ).delete()
        
        return JsonResponse({'liked': False, 'likes_count': post.likes_count})
    else:
        post.likes_count += 1
        post.save()
        
        # Beğeni bildirimi oluştur
        create_notification('like', request.user, post.author, post=post)
        
        return JsonResponse({'liked': True, 'likes_count': post.likes_count})


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
            
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent
            )
            post.comments_count += 1
            post.save()
            
            # Bildirim oluştur
            if parent:
                # Yanıt bildirimi (parent comment'in sahibine)
                create_notification('reply', request.user, parent.author, post=post, comment=comment)
            else:
                # Yorum bildirimi (post sahibine)
                create_notification('comment', request.user, post.author, post=post, comment=comment)
        
        # Eğer AJAX request değilse detay sayfasına yönlendir
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'comments_count': post.comments_count})
        
        return redirect('post_detail', post_id=post.id)
    return redirect('/feed/')


@login_required
def post_detail_view(request, post_id):
    """Post detay sayfası - tüm yorumları göster"""
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    
    # Kullanıcının beğenip beğenmediğini kontrol et
    user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    # Tüm yorumları al (parent yorumlar ve yanıtlar)
    comments = post.comments.filter(parent__isnull=True).select_related('author').prefetch_related(
        'replies__author'
    ).order_by('created_at')
    
    context = {
        'post': post,
        'user_has_liked': user_has_liked,
        'comments': comments,
    }
    
    return render(request, 'post_detail.html', context)


@login_required
def load_more_posts(request):
    """AJAX ile daha fazla post yükle"""
    page_number = request.GET.get('page', 1)
    feed_filter = request.GET.get('filter', 'all')
    
    # Aynı query'yi kullan
    posts_query = Post.objects.select_related('author', 'author__profile').prefetch_related(
        'comments__author', 'comments__author__profile'
    ).annotate(
        user_has_liked=Exists(
            Like.objects.filter(post=OuterRef('pk'), user=request.user)
        )
    )
    
    if feed_filter == 'following':
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        posts_query = posts_query.filter(
            Q(author__in=following_users) | Q(author=request.user)
        )
    
    posts_query = posts_query.order_by('-created_at')
    paginator = Paginator(posts_query, 10)
    posts_page = paginator.get_page(page_number)
    
    # HTML render et
    html = render_to_string('partials/post_list.html', {
        'posts': posts_page,
        'user': request.user,
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'has_next': posts_page.has_next(),
        'next_page': posts_page.next_page_number() if posts_page.has_next() else None,
    })


@login_required
def edit_post(request, post_id):
    """Post düzenleme"""
    post = get_object_or_404(Post, id=post_id)
    
    # Sadece post sahibi düzenleyebilir
    if post.author != request.user:
        return JsonResponse({'error': 'Bu postu düzenleme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Post içeriği boş olamaz.'}, status=400)
        
        post.content = content
        post.save()
        
        return JsonResponse({
            'success': True,
            'content': post.content,
            'message': 'Post başarıyla güncellendi!'
        })
    
    return JsonResponse({'error': 'Geçersiz istek.'}, status=400)


@login_required
def delete_post(request, post_id):
    """Post silme"""
    post = get_object_or_404(Post, id=post_id)
    
    # Sadece post sahibi silebilir
    if post.author != request.user:
        return JsonResponse({'error': 'Bu postu silme yetkiniz yok.'}, status=403)
    
    if request.method == 'POST':
        post.delete()
        return JsonResponse({
            'success': True,
            'message': 'Post başarıyla silindi!'
        })
    
    return JsonResponse({'error': 'Geçersiz istek.'}, status=400)


@login_required
def report_content(request):
    """İçerik raporlama (Post, Comment, User)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Geçersiz istek.'}, status=400)
    
    content_type_name = request.POST.get('content_type')  # 'post', 'comment', 'user'
    object_id = request.POST.get('object_id')
    reason = request.POST.get('reason')
    description = request.POST.get('description', '').strip()
    
    # Validasyon
    if not all([content_type_name, object_id, reason]):
        return JsonResponse({'error': 'Eksik bilgi.'}, status=400)
    
    # Content type belirle
    model_map = {
        'post': Post,
        'comment': Comment,
        'user': User,
    }
    
    if content_type_name not in model_map:
        return JsonResponse({'error': 'Geçersiz içerik tipi.'}, status=400)
    
    model_class = model_map[content_type_name]
    content_type = ContentType.objects.get_for_model(model_class)
    
    # Nesneyi kontrol et
    try:
        content_object = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        return JsonResponse({'error': 'İçerik bulunamadı.'}, status=404)
    
    # Kendi içeriğini raporlayamaz
    if content_type_name == 'post' and content_object.author == request.user:
        return JsonResponse({'error': 'Kendi postunuzu raporlayamazsınız.'}, status=400)
    elif content_type_name == 'comment' and content_object.author == request.user:
        return JsonResponse({'error': 'Kendi yorumunuzu raporlayamazsınız.'}, status=400)
    elif content_type_name == 'user' and content_object == request.user:
        return JsonResponse({'error': 'Kendinizi raporlayamazsınız.'}, status=400)
    
    # Aynı içeriği daha önce raporlamış mı kontrol et
    existing_report = Report.objects.filter(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id
    ).first()
    
    if existing_report:
        return JsonResponse({
            'error': 'Bu içeriği zaten raporladınız.',
            'status': existing_report.status
        }, status=400)
    
    # Rapor oluştur
    report = Report.objects.create(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id,
        reason=reason,
        description=description
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Rapor başarıyla gönderildi. Moderatörlerimiz inceleyecektir.',
        'report_id': report.id
    })
