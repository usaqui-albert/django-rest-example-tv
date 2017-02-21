from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import (
    Breeder, User, Veterinarian, AreaInterest, ProfileImage)


class UserAdmin(admin.ModelAdmin):
    '''
        Admin View for User
    '''
    list_display = ('username', 'email', 'id')


admin.site.register(User, UserAdmin)

admin.site.register(Breeder)
admin.site.register(Veterinarian)
admin.site.register(Permission)
admin.site.register(AreaInterest)
admin.site.register(ProfileImage)
