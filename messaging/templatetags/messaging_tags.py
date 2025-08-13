from django import template
from messaging.models import Message

register = template.Library()

@register.simple_tag(takes_context=True)
def unread_messages_count(context):
    request = context.get('request')
    if request and request.user.is_authenticated:
        return Message.objects.filter(conversation__participants=request.user, is_read=False).exclude(sender=request.user).count()
    return 0
