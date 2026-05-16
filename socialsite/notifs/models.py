from django.db import models
from django.contrib.auth.models import User
from posts.models import Post, Comment

class Notification(models.Model):
    """Kullanıcı bildirimleri"""
    
    NOTIFICATION_TYPES = (
        ('like', 'Beğeni'),
        ('comment', 'Yorum'),
        ('reply', 'Yanıt'),
        ('follow', 'Takip'),
        ('message', 'Mesaj'),
    )
    
    # Bildirim tipi ve taraflar
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    
    # İlişkili objeler (optional)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Durum ve zaman
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.sender.username} -> {self.receiver.username}"
    
    def get_message(self):
        """Bildirim mesajını döndürür"""
        if self.notification_type == 'like':
            return f"{self.sender.username} gönderinizi beğendi"
        elif self.notification_type == 'comment':
            return f"{self.sender.username} gönderinize yorum yaptı"
        elif self.notification_type == 'reply':
            return f"{self.sender.username} yorumunuza yanıt verdi"
        elif self.notification_type == 'follow':
            return f"{self.sender.username} sizi takip etmeye başladı"
        elif self.notification_type == 'message':
            return f"{self.sender.username} size mesaj gönderdi"
        return "Yeni bildirim"
    
    def get_icon(self):
        """Bildirim ikonu döndürür"""
        icons = {
            'like': '❤️',
            'comment': '💬',
            'reply': '↩️',
            'follow': '👤',
            'message': '✉️',
        }
        return icons.get(self.notification_type, '🔔')
    
    def get_url(self):
        """Bildirimin yönlendireceği URL'i döndürür"""
        if self.notification_type == 'message':
            return f'/messages/'
        elif self.post:
            return f'/api/posts/{self.post.id}/'
        elif self.notification_type == 'follow':
            return f'/profile/{self.sender.username}/'
        return '/feed/'
