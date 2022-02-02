from django.contrib import admin
from social.models import Idea, Follow


class IdeaAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['user', 'text', 'created', 'visibility']
    ordering = ['-created']
    search_fields = ['user__email', 'user__username', 'visibility']


class FollowAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['user', 'follower', 'status', 'created']
    ordering = ['-created',]
    search_fields = ['user__email', 'user__username', 'follower__email', 'follower__username']


admin.site.register(Idea, IdeaAdmin)
admin.site.register(Follow, FollowAdmin)
