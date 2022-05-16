# Django imports
from django.contrib import admin

# Project imports
from .models import Image, User

# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name','image_tag','photo']

admin.site.register(Image, ImageAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'career']

admin.site.register(User, UserAdmin)