from django.contrib import admin

from .models import Post, ImagePost


class PostAdmin(admin.ModelAdmin):
    '''
        Admin View for Post
    '''
    list_display = (
        'id', 'user', 'pet', 'visible_by_vet', 'visible_by_owner', 'get_likes')
    list_filter = ('visible_by_vet', 'visible_by_owner')
    search_fields = ('user', 'pet')


admin.site.register(Post, PostAdmin)
admin.site.register(ImagePost)
