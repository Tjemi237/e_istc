from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'notifications': list(notifications.values()), 'unread_count': unread_count})
    return render(request, 'notifications/notification_list.html', {'notifications': notifications, 'unread_count': unread_count})

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})