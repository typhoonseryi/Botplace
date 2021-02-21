from django.contrib import admin

from ugc.models import Profile, Place


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'name', 'lat', 'lon', 'file_id')


