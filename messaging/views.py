from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from users.models import User
from django.db.models import Q
from django.http import JsonResponse

@login_required
def inbox(request):
    conversations = request.user.conversations.all()
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
    # Marquer les messages comme lus
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
            return redirect('messaging:conversation_detail', conversation_id=conversation_id)
    return render(request, 'messaging/conversation_detail.html', {'conversation': conversation})

@login_required
def new_conversation(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient)
    if conversation.exists():
        return redirect('messaging:conversation_detail', conversation_id=conversation.first().id)
    else:
        new_conv = Conversation.objects.create()
        new_conv.participants.add(request.user, recipient)
        return redirect('messaging:conversation_detail', conversation_id=new_conv.id)

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(matricule__icontains=query)
        ).exclude(id=request.user.id).distinct()[:10] # Limite à 10 résultats
    
    users_data = [
        {
            'id': user.id,
            'name': f'{user.first_name} {user.last_name}',
            'email': user.email,
            'matricule': user.matricule
        } for user in users
    ]
    return JsonResponse({'users': users_data})