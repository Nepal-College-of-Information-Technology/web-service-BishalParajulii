from django.contrib import admin
from .models import ChatMessage , Message
from django.utils.html import format_html




class GrpMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'file_link')

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "-"
    file_link.short_description = 'File'

admin.site.register(ChatMessage, GrpMessageAdmin)



class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp', 'file_link')

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "-"
    file_link.short_description = 'File'

admin.site.register(Message, MessageAdmin)
