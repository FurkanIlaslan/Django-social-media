from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from notifs.utils import create_notification
from .models import EmailVerificationToken, Profile, Follow
from .forms import ProfileEditForm
from posts.models import Post


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/feed/')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            return render(request, 'auth/login.html', {
                'username': username,
                'error': '⚠️ Kullanıcı adı ve şifre boş bırakılamaz.',
            })
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return render(request, 'auth/login.html', {
                    'username': username,
                    'error': '📧 Hesabınız henüz onaylanmamış. Lütfen e-postanızı kontrol edin.',
                })
            login(request, user)
            return redirect('/feed/')
        
        return render(request, 'auth/login.html', {
            'username': username,
            'error': '❌ Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin.',
        })
    return render(request, 'auth/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/feed/')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        errors = []

        if not username or not email or not password1:
            errors.append('Tum alanlari doldurun.')
        if len(password1) < 8:
            errors.append('Parola en az 8 karakter olmalidir.')
        if password1 != password2:
            errors.append('Parolalar eslesmiyyor.')
        if User.objects.filter(username=username).exists():
            errors.append('Bu kullanici adi zaten alinmis.')
        if email and User.objects.filter(email=email).exists():
            errors.append('Bu e-posta zaten kayitli.')

        if errors:
            return render(request, 'auth/signup.html', {
                'errors': errors, 'username': username, 'email': email,
            })

        user = User.objects.create_user(username=username, email=email, password=password1)
        # Production'da email doğrulama olmadan direkt aktif et
        user.is_active = True  # Demo için direkt aktif
        user.save()

        # Email doğrulama (opsiyonel - email ayarları varsa)
        try:
            if settings.EMAIL_HOST_USER:  # Email ayarları varsa
                token_obj = EmailVerificationToken.objects.create(user=user)
                activate_url = f"{settings.SITE_URL}/accounts/activate/{token_obj.token}/"

                send_mail(
                    subject='SocialSite - E-posta adresinizi onaylayin',
                    message=(
                        f"Merhaba {username},\n\n"
                        f"Kaydınızı tamamlamak için asagidaki baglantiya tiklayin:\n\n"
                        f"{activate_url}\n\n"
                        f"--- SocialSite Ekibi"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                return render(request, 'auth/email_sent.html', {'email': email})
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Email gönderimi başarısız olursa veya email ayarları yoksa direkt login
        login(request, user)
        return redirect('/feed/')

    return render(request, 'auth/signup.html')


def activate_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    user = token_obj.user

    if user.is_active:
        return redirect('/login/')

    user.is_active = True
    user.save()
    token_obj.delete()

    return render(request, 'auth/activated.html', {'username': user.username})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request, username=None):
    """Kullanıcı profilini görüntüle"""
    if username:
        # Başka bir kullanıcının profilini görüntüle
        profile_user = get_object_or_404(User, username=username)
    else:
        # Kendi profilini görüntüle
        profile_user = request.user
    
    # Profil yoksa oluştur
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    # Kullanıcının postlarını getir
    posts = profile_user.posts.all().order_by('-created_at')
    
    # Takip durumunu kontrol et
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'posts_count': posts.count(),
        'is_own_profile': request.user == profile_user,
        'is_following': is_following,
    }
    
    return render(request, 'profile.html', context)


@login_required
def edit_profile_view(request):
    """Profil düzenleme sayfası"""
    # Profil yoksa oluştur
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})


@login_required
@require_POST
def follow_user(request, username):
    """Kullanıcıyı takip et"""
    user_to_follow = get_object_or_404(User, username=username)
    
    # Kendini takip edemez
    if request.user == user_to_follow:
        return JsonResponse({'error': 'Kendinizi takip edemezsiniz'}, status=400)
    
    # Zaten takip ediyorsa hata döndür
    if Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
        return JsonResponse({'error': 'Bu kullanıcıyı zaten takip ediyorsunuz'}, status=400)
    
    # Takip et
    Follow.objects.create(follower=request.user, following=user_to_follow)
    
    # Takip bildirimi oluştur
    create_notification('follow', request.user, user_to_follow)
    
    # Güncel sayıları hesapla
    followers_count = Follow.objects.filter(following=user_to_follow).count()
    following_count = Follow.objects.filter(follower=user_to_follow).count()
    
    return JsonResponse({
        'success': True,
        'is_following': True,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
@require_POST
def unfollow_user(request, username):
    """Kullanıcıyı takipten çık"""
    user_to_unfollow = get_object_or_404(User, username=username)
    
    # Takibi kaldır
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    
    # Güncel sayıları hesapla
    followers_count = Follow.objects.filter(following=user_to_unfollow).count()
    following_count = Follow.objects.filter(follower=user_to_unfollow).count()
    
    return JsonResponse({
        'success': True,
        'is_following': False,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
@require_POST
def toggle_follow(request, user_id):
    """Kullanıcıyı takip et/takipten çık (toggle)"""
    user_to_toggle = get_object_or_404(User, id=user_id)
    
    # Kendini takip edemez
    if request.user == user_to_toggle:
        return JsonResponse({'error': 'Kendinizi takip edemezsiniz'}, status=400)
    
    # Takip durumunu kontrol et
    follow = Follow.objects.filter(follower=request.user, following=user_to_toggle).first()
    
    if follow:
        # Takipten çık
        follow.delete()
        is_following = False
    else:
        # Takip et
        Follow.objects.create(follower=request.user, following=user_to_toggle)
        is_following = True
        
        # Takip bildirimi oluştur
        create_notification('follow', request.user, user_to_toggle)
    
    return JsonResponse({
        'success': True,
        'following': is_following,
    })


@login_required
def search_view(request):
    """Kullanıcı ve post arama"""
    query = request.GET.get('q', '').strip()
    
    users = []
    posts = []
    
    if query:
        # Kullanıcı ara (username, first_name, last_name)
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile')[:10]
        
        # Post ara (içerik)
        posts = Post.objects.filter(
            content__icontains=query
        ).select_related('author').prefetch_related('comments')[:20]
    
    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'users_count': len(users),
        'posts_count': len(posts),
    }
    
    return render(request, 'search.html', context)
