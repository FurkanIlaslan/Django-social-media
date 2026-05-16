from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.http import JsonResponse
from .models import Conversation, Message
from notifs.utils import create_notification

@login_required
def conversation_list(request):
    """Kullanıcının tüm konuşmalarını listeler"""
    # Kullanıcının dahil olduğu tüm konuşmaları getir
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Her konuşma için gerekli bilgileri hazırla
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_user(request.user)
        last_message = conv.get_last_message()
        unread_count = conv.get_unread_count(request.user)
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    context = {
        'conversation_data': conversation_data,
    }
    return render(request, 'chat/conversation_list.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Belirli bir konuşmanın detayını gösterir"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Kullanıcının bu konuşmaya erişimi olup olmadığını kontrol et
    if request.user not in conversation.participants.all():
        return redirect('conversation_list')
    
    # Konuşmadaki tüm mesajları getir
    messages = conversation.messages.select_related('sender', 'receiver').all()
    
    # Kullanıcının aldığı okunmamış mesajları okundu olarak işaretle
    Message.objects.filter(
        conversation=conversation,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    other_user = conversation.get_other_user(request.user)
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
    }
    return render(request, 'chat/conversation_detail.html', context)

@login_required
def send_message(request, conversation_id):
    """Konuşmaya yeni mesaj gönderir"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Kullanıcının bu konuşmaya erişimi olup olmadığını kontrol et
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    # Alıcıyı bul
    receiver = conversation.get_other_user(request.user)
    
    # Mesajı oluştur
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=receiver,
        content=content
    )
    
    # Konuşmanın updated_at'ini güncelle
    conversation.save()
    
    # Mesaj bildirimi oluştur
    create_notification('message', request.user, receiver)
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_own': message.sender == request.user
        }
    })

@login_required
def start_conversation(request, username):
    """Belirli bir kullanıcıyla yeni konuşma başlatır veya mevcut konuşmaya yönlendirir"""
    other_user = get_object_or_404(User, username=username)
    
    # Kendisiyle konuşma başlatamaz
    if other_user == request.user:
        return redirect('conversation_list')
    
    # Bu iki kullanıcı arasında mevcut bir konuşma var mı kontrol et
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('conversation_detail', conversation_id=existing_conversation.id)
    
    # Yeni konuşma oluştur
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
def get_new_messages(request, conversation_id):
    """AJAX ile yeni mesajları getirir"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Kullanıcının bu konuşmaya erişimi olup olmadığını kontrol et
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    last_message_id = request.GET.get('last_message_id', 0)
    
    # Son mesaj ID'sinden sonraki mesajları getir
    new_messages = Message.objects.filter(
        conversation=conversation,
        id__gt=last_message_id
    ).select_related('sender')
    
    # Yeni mesajları okundu olarak işaretle
    Message.objects.filter(
        conversation=conversation,
        receiver=request.user,
        is_read=False,
        id__gt=last_message_id
    ).update(is_read=True)
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender': msg.sender.username,
        'created_at': msg.created_at.strftime('%H:%M'),
        'is_own': msg.sender == request.user
    } for msg in new_messages]
    
    return JsonResponse({'messages': messages_data})
