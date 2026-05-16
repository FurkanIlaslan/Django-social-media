from .models import Notification

def create_notification(notification_type, sender, receiver, post=None, comment=None):
    """Yeni bildirim oluşturur (kendine bildirim göndermez)"""
    if sender == receiver:
        return None
    
    # Aynı bildirim varsa tekrar oluşturma (özellikle like için)
    if notification_type == 'like' and post:
        existing = Notification.objects.filter(
            notification_type='like',
            sender=sender,
            receiver=receiver,
            post=post
        ).first()
        if existing:
            return existing
    
    notification = Notification.objects.create(
        notification_type=notification_type,
        sender=sender,
        receiver=receiver,
        post=post,
        comment=comment
    )
    return notification
