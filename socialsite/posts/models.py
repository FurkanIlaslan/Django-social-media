from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} -> {self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam veya Yanıltıcı'),
        ('harassment', 'Taciz veya Zorbalık'),
        ('hate_speech', 'Nefret Söylemi'),
        ('violence', 'Şiddet veya Tehlikeli İçerik'),
        ('nudity', 'Çıplaklık veya Cinsel İçerik'),
        ('false_info', 'Yanlış Bilgi'),
        ('other', 'Diğer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('reviewing', 'İnceleniyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_moderated')
    moderator_note = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Report by {self.reporter.username} - {self.get_reason_display()} ({self.status})"
    
    def get_reported_item_display(self):
        """Raporlanan öğenin tipini ve içeriğini göster"""
        if isinstance(self.content_object, Post):
            return f"Post: {self.content_object.content[:50]}"
        elif isinstance(self.content_object, Comment):
            return f"Comment: {self.content_object.content[:50]}"
        elif isinstance(self.content_object, User):
            return f"User: {self.content_object.username}"
        return "Unknown"
