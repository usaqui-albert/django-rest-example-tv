from django.contrib import admin

from .models import Pet


class PetAdmin(admin.ModelAdmin):
    '''
        Admin View for Pet
    '''
    list_display = (
        'user', 'id', 'name', 'fixed', 'birth_year', 'pet_type', 'breed',
        'gender')
    list_filter = ('fixed',)
    search_fields = ('user',)


admin.site.register(Pet, PetAdmin)
