import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='Biyografi')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Profil Fotoğrafı')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='Website')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Konum')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profiller'

    def __str__(self):
        return f"{self.user.username}'in profili"

    def get_posts_count(self):
        return self.user.posts.count()

    def get_followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    def get_following_count(self):
        return Follow.objects.filter(follower=self.user).count()


class Follow(models.Model):
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following', 
        verbose_name='Takip Eden'
    )
    following = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers', 
        verbose_name='Takip Edilen'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Takip Tarihi')

    class Meta:
        verbose_name = 'Takip'
        verbose_name_plural = 'Takipler'
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


# Kullanıcı oluşturulduğunda otomatik olarak profil oluştur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
