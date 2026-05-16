from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def notifications_view(request):
    """Tüm bildirimleri listeler"""
    notifications = Notification.objects.filter(
        receiver=request.user
    ).select_related('sender', 'post', 'comment')[:50]
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifs/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Bildirimi okundu olarak işaretle"""
    try:
        notification = Notification.objects.get(id=notification_id, receiver=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@login_required
@require_POST
def mark_all_read(request):
    """Tüm bildirimleri okundu olarak işaretle"""
    Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
def get_unread_count(request):
    """Okunmamış bildirim sayısını döndürür"""
    count = Notification.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})
