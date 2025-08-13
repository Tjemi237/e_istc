from django.contrib import admin
from .models import SujetDiscussion, MessageForum

@admin.register(SujetDiscussion)
class SujetDiscussionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'auteur', 'cree_le', 'mis_a_jour_le')
    list_filter = ('cours', 'auteur')
    search_fields = ('titre', 'auteur__username')

@admin.register(MessageForum)
class MessageForumAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'auteur', 'cree_le')
    list_filter = ('sujet__cours', 'auteur')
    search_fields = ('contenu', 'auteur__username')