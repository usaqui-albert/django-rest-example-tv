from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import (
    Breeder, User, Veterinarian, AreaInterest)
from .mixins import Group

admin.site.register(Breeder)
admin.site.register(Veterinarian)
admin.site.register(User)
admin.site.register(Permission)
admin.site.register(Group)
admin.site.register(AreaInterest)
