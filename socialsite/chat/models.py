from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class Conversation(models.Model):
    """İki kullanıcı arasındaki konuşma"""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        users = list(self.participants.all()[:2])
        if len(users) == 2:
            return f"{users[0].username} - {users[1].username}"
        return f"Conversation {self.id}"
    
    def get_other_user(self, user):
        """Mevcut kullanıcının dışındaki diğer kullanıcıyı döndürür"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Konuşmanın son mesajını döndürür"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Kullanıcının okunmamış mesaj sayısını döndürür"""
        return self.messages.filter(receiver=user, is_read=False).count()

class Message(models.Model):
    """Kullanıcılar arasındaki mesajlar"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:30]}"
